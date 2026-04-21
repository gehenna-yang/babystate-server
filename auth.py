from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import get_db
import models
import uuid

# [환경변수 값]
SECRET_KEY = "babystatekey"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# [토큰 생성 함수]
def create_tokens(user_id: str):
    # Access Token: 30분 유효
    access_exp = datetime.now() + timedelta(minutes=30)
    access_token = jwt.encode({"sub": user_id, "exp": access_exp, "type": "access"}, SECRET_KEY, algorithm=ALGORITHM)
    
    # Refresh Token: 1일 유효
    refresh_exp = datetime.now() + timedelta(days=1)
    refresh_token = jwt.encode({"sub": user_id, "exp": refresh_exp, "type": "refresh"}, SECRET_KEY, algorithm=ALGORITHM)
    
    return access_token, refresh_token, refresh_exp

# [토큰 검증]
def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="토큰이 만료되었습니다.")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")
    
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user_id_str = verify_access_token(token)
    user = db.query(models.User).filter(models.User.id == uuid.UUID(user_id_str)).first()
    if user is None:
        raise HTTPException(status_code=401, detail="사용자를 찾을 수 없습니다.")
    return user