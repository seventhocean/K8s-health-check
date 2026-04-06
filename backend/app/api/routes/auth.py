"""Authentication API routes"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.schemas.auth import UserLogin, Token, UserResponse, UserCreate, UserUpdate
from app.models.auth import User, AuditLog
from app.services.database import get_db
from app.services.auth_service import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_token,
    get_current_user,
)

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()


@router.post("/login", response_model=Token)
async def login(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    """User login"""
    # Find user
    result = await db.execute(select(User).where(User.username == login_data.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is disabled"
        )

    # Update last login
    from datetime import datetime
    user.last_login_at = datetime.utcnow()
    await db.commit()

    # Create access token
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=timedelta(minutes=1440)  # 24 hours
    )

    # Log audit
    if request:
        audit_log = AuditLog(
            user_id=user.id,
            username=user.username,
            action="login",
            resource_type="User",
            resource_name=user.username,
            ip_address=request.client.host if request.client else None,
            status="success"
        )
        db.add(audit_log)
        await db.commit()

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.model_validate(user)
    }


@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    """User registration"""
    # Check if username exists
    result = await db.execute(select(User).where(User.username == user_data.username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Check if email exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        phone=user_data.phone,
        role=user_data.role,
        hashed_password=hashed_password,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Log audit
    if request:
        audit_log = AuditLog(
            user_id=new_user.id,
            username=new_user.username,
            action="create",
            resource_type="User",
            resource_name=new_user.username,
            ip_address=request.client.host if request.client else None,
            status="success"
        )
        db.add(audit_log)
        await db.commit()

    return UserResponse.model_validate(new_user)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    return current_user


@router.post("/logout")
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """User logout (token invalidation should be handled client-side)"""
    # Log audit
    audit_log = AuditLog(
        user_id=current_user.id,
        username=current_user.username,
        action="logout",
        resource_type="User",
        resource_name=current_user.username,
        ip_address=request.client.host if request.client else None,
        status="success"
    )
    db = request.state.db if hasattr(request, 'state') else None
    if db:
        db.add(audit_log)
        await db.commit()

    return {"message": "Logged out successfully"}
