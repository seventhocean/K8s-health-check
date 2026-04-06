"""Pydantic schemas for authentication"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


# User schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    phone: Optional[str] = None
    role: str = "viewer"


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None


# Audit log schemas
class AuditLogBase(BaseModel):
    action: str
    resource_type: str
    resource_name: str
    namespace: Optional[str] = None
    details: Optional[str] = None
    status: str = "success"


class AuditLogCreate(AuditLogBase):
    user_id: Optional[int] = None
    username: Optional[str] = None
    ip_address: Optional[str] = None


class AuditLogResponse(AuditLogBase):
    id: int
    user_id: Optional[int] = None
    username: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
