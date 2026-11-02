from typing import Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database_sql import get_db
from app.models.db_models import InstitutionProfile, StudentProfile, User, UserRole
from app.utils.security import create_access_token, get_current_user, hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])

DEMO_USERS = {
    "admin@skillbridge.local": {"password": "admin123", "full_name": "Admin User", "role": "admin"},
    "student@skillbridge.local": {"password": "student123", "full_name": "Student User", "role": "student"},
    "employer@skillbridge.local": {"password": "employer123", "full_name": "Employer User", "role": "employer"},
    "institution@skillbridge.local": {"password": "institution123", "full_name": "Institution User", "role": "institution"},
}
LOCAL_USERS = {}


def authenticate_demo_user(email: str, password: str):
    normalized_email = (email or "").strip().lower()
    user = DEMO_USERS.get(normalized_email)
    if user and user["password"] == password:
        return {
            "id": f"demo-{user['role']}",
            "email": normalized_email,
            "full_name": user["full_name"],
            "role": user["role"],
        }

    local_user = LOCAL_USERS.get(normalized_email)
    if not local_user or not verify_password(password, local_user["password_hash"]):
        return None
    return {
        "id": local_user["id"],
        "email": normalized_email,
        "full_name": local_user["full_name"],
        "role": local_user["role"],
    }


class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str
    role: str  # student | employer | institution | admin
    college_name: Optional[str] = None
    institution_name: Optional[str] = None  # for role=institution


class LoginRequest(BaseModel):
    email: str
    password: str


def _user_out(user: User) -> dict:
    return {"id": user.id, "email": user.email, "full_name": user.full_name, "role": user.role.value}


@router.post("/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    if req.role not in [r.value for r in UserRole]:
        raise HTTPException(status_code=400, detail=f"Invalid role. Must be one of: {[r.value for r in UserRole]}")

    normalized_email = req.email.strip().lower()
    if normalized_email in DEMO_USERS or normalized_email in LOCAL_USERS:
        raise HTTPException(status_code=409, detail="An account with this email already exists")

    try:
        existing = db.query(User).filter(User.email == normalized_email).first()
        if existing:
            raise HTTPException(status_code=409, detail="An account with this email already exists")

        user = User(
            email=normalized_email,
            password_hash=hash_password(req.password),
            role=UserRole(req.role),
            full_name=req.full_name,
        )
        db.add(user)
        db.flush()

        if user.role == UserRole.student:
            db.add(StudentProfile(user_id=user.id, college_name=req.college_name))
        elif user.role == UserRole.institution:
            db.add(InstitutionProfile(user_id=user.id, institution_name=req.institution_name or req.full_name))

        db.commit()
        db.refresh(user)
        token = create_access_token(user.id, user.role.value, user.email)
        return {"access_token": token, "token_type": "bearer", "user": _user_out(user)}
    except HTTPException:
        raise
    except Exception:
        local_user = {
            "id": f"local-{uuid.uuid4()}",
            "email": normalized_email,
            "password_hash": hash_password(req.password),
            "full_name": req.full_name,
            "role": req.role,
        }
        LOCAL_USERS[normalized_email] = local_user
        user_out = {key: local_user[key] for key in ("id", "email", "full_name", "role")}
        token = create_access_token(local_user["id"], local_user["role"], local_user["email"])
        return {"access_token": token, "token_type": "bearer", "user": user_out}


@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    normalized_email = (req.email or "").strip().lower()
    demo_user = authenticate_demo_user(normalized_email, req.password)
    if demo_user:
        token = create_access_token(demo_user["id"], demo_user["role"], demo_user["email"])
        return {"access_token": token, "token_type": "bearer", "user": demo_user}

    try:
        user = db.query(User).filter(User.email == normalized_email).first()
        if not user or not verify_password(req.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Incorrect email or password")
        if not user.is_active:
            raise HTTPException(status_code=403, detail="This account has been deactivated")

        token = create_access_token(user.id, user.role.value, user.email)
        return {"access_token": token, "token_type": "bearer", "user": _user_out(user)}
    except Exception as exc:
        if isinstance(exc, HTTPException):
            raise
        raise HTTPException(status_code=503, detail="Authentication service unavailable. Please ensure PostgreSQL is running or use a demo login.")


@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return _user_out(current_user)
