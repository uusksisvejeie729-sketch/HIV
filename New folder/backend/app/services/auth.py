from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import settings
from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# In-memory reset tokens for demo (use Redis/email in production)
_reset_tokens: dict[str, tuple[str, datetime]] = {}


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    return jwt.encode(
        {"sub": subject, "exp": expire},
        settings.secret_key,
        algorithm=settings.algorithm,
    )


def decode_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload.get("sub")
    except JWTError:
        return None


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def create_reset_token(email: str) -> str:
    import secrets

    token = secrets.token_urlsafe(32)
    _reset_tokens[token] = (email, datetime.now(timezone.utc) + timedelta(hours=1))
    return token


def consume_reset_token(token: str, email: str) -> bool:
    entry = _reset_tokens.get(token)
    if not entry:
        return False
    stored_email, expires = entry
    if stored_email != email or datetime.now(timezone.utc) > expires:
        return False
    del _reset_tokens[token]
    return True
