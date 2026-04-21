from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timezone, timedelta
from typing import List, Optional
import uuid
import models
import auth
from database import get_db

KST = timezone(timedelta(hours=9))

router = APIRouter(prefix="/babys", tags=["Babys"])

class BabyCreate(BaseModel):
    nickname: str
    birth: datetime
    memo: Optional[str] = None

class BabyResponse(BabyCreate):
    id: uuid.UUID
    created_at: datetime
    class Config:
        from_attributes = True

# [아기 목록]
@router.get("", response_model=List[BabyResponse])
def get_babys(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return db.query(models.Babys).filter(models.Babys.created_user == current_user.id).order_by(models.Babys.created_at.asc()).all()

# [아기 등록]
@router.post("/register")
def create_baby(baby_data: BabyCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    
    birth_dt = baby_data.birth
    if birth_dt.tzinfo is None:
        birth_dt = birth_dt.replace(tzinfo=KST)

    new_baby = models.Babys(
        nickname=baby_data.nickname,
        birth=birth_dt,
        memo=baby_data.memo,
        created_user=current_user.id,
        updated_user=current_user.id
    )
    db.add(new_baby)
    db.commit()
    db.refresh(new_baby)
    return new_baby

# [아기 정보 수정]
@router.patch("/{baby_id}")
def update_baby(baby_id: uuid.UUID, update_data: dict, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    baby = db.query(models.Babys).filter(
        models.Babys.id == baby_id,
        models.Babys.created_user == current_user.id
    ).first()
    
    if not baby:
        raise HTTPException(status_code=404, detail="아기 정보를 찾을 수 없습니다.")
    
        
    if "nickname" in update_data: baby.nickname = update_data["nickname"]
    if "birth" in update_data: 
        birth_dt = datetime.fromisoformat(update_data["birth"])
        if birth_dt.tzinfo is None:
            birth_dt = birth_dt.replace(tzinfo=KST)
        baby.birth = birth_dt
    if "memo" in update_data: baby.memo = update_data["memo"]
    
    baby.updated_user = current_user.id
    baby.updated_at = datetime.now(KST)
    
    db.commit()
    db.refresh(baby)
    return baby