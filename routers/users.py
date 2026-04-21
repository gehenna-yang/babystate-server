from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
import models
import auth
from database import get_db

router = APIRouter(tags=["Users"])

class UserRegister(BaseModel):
    account_id: str
    account_pwd: str
    nickname: str

class UserLogin(BaseModel):
    account_id: str
    account_pwd: str

# [회원가입]
@router.post("/signup")
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    
    existing_user = db.query(models.User).filter(models.User.account_id == user_data.account_id).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="이미 존재하는 아이디입니다.")
    
    hashed_pw = auth.hash_password(user_data.account_pwd)
    new_user = models.User(
        account_id=user_data.account_id,
        account_pwd=hashed_pw,
        nickname=user_data.nickname
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "회원가입 완료", "user_id": new_user.id}

# [유저 로그인]
@router.post("/login")
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    
    user = db.query(models.User).filter(models.User.account_id == user_data.account_id).first()
    if not user or not auth.verify_password(user_data.account_pwd, user.account_pwd):
        raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 틀렸습니다.")

    access_token, refresh_token, refresh_exp = auth.create_tokens(str(user.id))

    db.query(models.RefreshToken).filter(models.RefreshToken.user_id == user.id).delete()
    
    db_token = models.RefreshToken(
        user_id=user.id,
        token_val=refresh_token,
        expires_at=refresh_exp
    )
    db.add(db_token)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

# [토큰 재발급]
@router.post("/refresh")
def refresh(refresh_token: str = Body(..., embed=True), db: Session = Depends(get_db)):
    
    db_token = db.query(models.RefreshToken).filter(models.RefreshToken.token_val == refresh_token).first()
    
    if not db_token:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")

    if db_token.expires_at.replace(tzinfo=None) < datetime.now():
        db.delete(db_token)
        db.commit()
        raise HTTPException(status_code=401, detail="세션이 만료되었습니다. 다시 로그인하세요.")

    new_access_token, _, _ = auth.create_tokens(str(db_token.user_id))
    
    return {"access_token": new_access_token, "token_type": "bearer"}
# [내 정보 불러오기]
@router.get("/user/me")
def get_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

# [내 정보 수정]
@router.patch("/user/me")
def update_me(
    update_data: dict = Body(...), 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(auth.get_current_user)
):
    if "nickname" in update_data:
        current_user.nickname = update_data["nickname"]
        
    if "new_password" in update_data and "old_password" in update_data:
        if not auth.verify_password(update_data["old_password"], current_user.account_pwd):
            raise HTTPException(status_code=400, detail="기존 비밀번호가 일치하지 않습니다.")
        current_user.account_pwd = auth.hash_password(update_data["new_password"])
        
    if "memo" in update_data:
        current_user.memo = update_data["memo"]
    
    current_user.updated_at = datetime.now()
    db.commit()
    db.refresh(current_user)
    return current_user