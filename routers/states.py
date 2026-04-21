from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, date, time, timezone, timedelta
from typing import Optional
import uuid
import models
import auth
from database import get_db

KST = timezone(timedelta(hours=9))

router = APIRouter(prefix="/states", tags=["States"])

class StateCreate(BaseModel):
    baby_id: str
    type: str
    value: dict
    memo: Optional[str] = None

# [상태 등록 API]
@router.post("/")
def create_state(
    state_data: StateCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    new_state = models.States(
        baby_id=uuid.UUID(state_data.baby_id),
        type=state_data.type,
        value=state_data.value,
        memo=state_data.memo,
        created_user=current_user.id
    )
    db.add(new_state)
    db.commit()
    db.refresh(new_state)
    return new_state

# [상태 목록 조회 API (날짜 필터링 포함)]
@router.get("/{baby_id}")
def get_states(
    baby_id: str,
    target_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    query = db.query(models.States).filter(models.States.baby_id == uuid.UUID(baby_id))
    
    if target_date:
        start_dt = datetime.combine(target_date, time.min)
        end_dt = datetime.combine(target_date, time.max)
        query = query.filter(models.States.created_at.between(start_dt, end_dt))
    
    return query.order_by(models.States.created_at.desc()).all()

# [상태 기록 수정 API]
@router.patch("/{state_id}")
def update_state(
    state_id: int, 
    update_data: dict,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    state = db.query(models.States).filter(
        models.States.id == state_id, 
        models.States.created_user == current_user.id
    ).first()
    
    if not state:
        raise HTTPException(status_code=404, detail="기록을 찾을 수 없거나 권한이 없습니다.")
    
    if "type" in update_data: state.type = update_data["type"]
    if "value" in update_data: state.value = update_data["value"]
    if "memo" in update_data: state.memo = update_data["memo"]
    
    state.updated_at = datetime.now(KST)
    state.updated_user = current_user.id
    
    db.commit()
    db.refresh(state)
    return state

# [상태 기록 삭제 API]
@router.delete("/states/{state_id}")
def delete_state(
    state_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    state = db.query(models.States).filter(
        models.States.id == state_id, 
        models.States.created_user == current_user.id
    ).first()
    
    if not state:
        raise HTTPException(status_code=404, detail="기록을 찾을 수 없거나 권한이 없습니다.")
    
    db.delete(state)
    db.commit()
    return {"message": "기록이 성공적으로 삭제되었습니다."}

