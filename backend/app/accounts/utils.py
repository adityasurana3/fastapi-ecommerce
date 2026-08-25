import uuid

from passlib.context import CryptContext
from datetime import timedelta, datetime, timezone
import jwt
from decouple import config

from app.accounts.schema import UserOut
from sqlalchemy.ext.asyncio import AsyncSession
from app.accounts.models import RefreshToken

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
JWT_SECRET = config("JWT_SECRET")
JWT_ALGORITHM = config("JWT_ALGORITHM")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires: timedelta = None) -> str:
    to_encode = data.copy()
    expires = datetime.now(timezone.utc) + (expires or timedelta(minutes=15))
    to_encode.update({"exp": expires})
    return jwt.encode(to_encode, JWT_SECRET, JWT_ALGORITHM)


async def create_token(session: AsyncSession, user: UserOut):
    access_token = create_access_token(data={"sub": user.id})
    refresh_token_str = str(uuid.uuid4())
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    refresh_token = RefreshToken(
        user_id=user.id, tokens=refresh_token_str, expires_at=expires_at
    )
    session.add(refresh_token)
    await session.commit()
    return {
        "access_token": access_token,
        "refresh_token": refresh_token_str,
        "token_type": "bearer",
    }
