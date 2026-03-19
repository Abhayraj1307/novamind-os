import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from app.db.database import get_db
from app.db.models import User
from app.core.auth import (
    get_password_hash,
    verify_password,
    validate_password_strength
)

router = APIRouter(tags=["auth"])


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str = "User"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/register")
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    err = validate_password_strength(payload.password)
    if err:
        raise HTTPException(status_code=400, detail=err)

    new_user = User(
        user_id=str(uuid.uuid4()),
        email=payload.email,
        hashed_password=get_password_hash(payload.password),
        full_name=payload.full_name,
        is_admin=False,
        is_verified=True
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "status": "created",
        "user_id": new_user.user_id,
        "name": new_user.full_name,
        "is_admin": new_user.is_admin
    }


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    return {
        "status": "ok",
        "user_id": user.user_id,
        "name": user.full_name,
        "is_admin": user.is_admin
    }
