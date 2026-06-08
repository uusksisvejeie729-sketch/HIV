from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.activity_log import ActivityLog
from app.models.user import User
from app.schemas.user import (
    PasswordResetConfirm,
    PasswordResetRequest,
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)
from app.services.auth import (
    consume_reset_token,
    create_access_token,
    create_reset_token,
    get_user_by_email,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _log(db: Session, user_id: int | None, activity: str, details: str | None = None):
    db.add(ActivityLog(user_id=user_id, activity=activity, details=details))


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    if get_user_by_email(db, payload.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        name=payload.name,
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
        role="user",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    _log(db, user.id, "register", f"User {user.email} registered")
    db.commit()
    token = create_access_token(user.email)
    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = get_user_by_email(db, payload.email.lower())
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    _log(db, user.id, "login")
    db.commit()
    return TokenResponse(
        access_token=create_access_token(user.email),
        user=UserResponse.model_validate(user),
    )


@router.post("/logout")
def logout(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _log(db, current_user.id, "logout")
    db.commit()
    return {"message": "Logged out successfully"}


@router.post("/reset-password/request")
def request_password_reset(payload: PasswordResetRequest, db: Session = Depends(get_db)):
    user = get_user_by_email(db, payload.email.lower())
    if not user:
        return {"message": "If the email exists, a reset token has been issued"}
    token = create_reset_token(user.email)
    # Demo: return token in response (production: send via email)
    return {
        "message": "Reset token generated (demo mode)",
        "reset_token": token,
    }


@router.post("/reset-password/confirm")
def confirm_password_reset(payload: PasswordResetConfirm, db: Session = Depends(get_db)):
    if not consume_reset_token(payload.token, payload.email.lower()):
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    user = get_user_by_email(db, payload.email.lower())
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.password_hash = hash_password(payload.new_password)
    _log(db, user.id, "password_reset")
    db.commit()
    return {"message": "Password updated successfully"}
