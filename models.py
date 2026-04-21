# models.py
from sqlalchemy import Column, String, DateTime, ForeignKey, BigInteger, Identity
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid
from database import Base 

class User(Base):
    __tablename__ = "user"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(String, unique=True, index=True, nullable=False)
    account_pwd = Column(String, nullable=False)
    nickname = Column(String, nullable=False)
    photo = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    memo = Column(String)

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    token_val = Column(String, unique=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Babys(Base):
    __tablename__ = "babys"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_user = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    updated_user = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    nickname = Column(String, nullable=False)
    birth = Column(DateTime(timezone=True), server_default=func.now())
    memo = Column(String)

class States(Base):
    __tablename__ = "states"
    id = Column(BigInteger, Identity(always=True), primary_key=True)
    type = Column(String, nullable=False)
    value = Column(JSONB, nullable=False)
    baby_id = Column(UUID(as_uuid=True), ForeignKey("babys.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_user = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    memo = Column(String)