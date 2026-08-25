from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserRead, Token
from app.auth.security import get_password_hash, verify_password, create_access_token
from app.auth.deps import get_current_user
from app.config import get_settings

router = APIRouter()
settings = get_settings()

@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)) -> Any:
    """Register a new user."""
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    
    # Optional: ensure demo users setup doesn't get overwritten, but usually this is standard register
    user = User(
        name=user_in.name,
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        phone=user_in.phone,
        college=user_in.college,
        student_id=user_in.student_id,
        role="USER" # By default everyone is a USER
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=Token)
def login_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """OAuth2 compatible token login, get an access token for future requests"""
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    access_token_expires = timedelta(minutes=settings.jwt_expire_minutes)
    return {
        "access_token": create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.post("/logout")
def logout() -> Any:
    """Logout endpoint. For JWT, client drops the token."""
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserRead)
def read_user_me(current_user: User = Depends(get_current_user)) -> Any:
    """Get current user."""
    return current_user
