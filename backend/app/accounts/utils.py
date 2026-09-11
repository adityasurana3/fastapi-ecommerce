from typing import Any
import uuid

from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from passlib.context import CryptContext
from datetime import timedelta, datetime, timezone
from decouple import config
from sqlalchemy import select

from app.accounts.schema import UserOut
from sqlalchemy.ext.asyncio import AsyncSession
from app.accounts.models import RefreshToken
from jose import jwt, ExpiredSignatureError, JWTError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
JWT_SECRET = config("JWT_SECRET")
JWT_ALGORITHM = config("JWT_ALGORITHM")
ACCESS_TOKEN_TTL = timedelta(minutes=15)
REFRESH_TOKEN_TTL = timedelta(days=14)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires: timedelta = None) -> str:
    to_encode = data.copy()
    expires = datetime.now(timezone.utc) + (expires or ACCESS_TOKEN_TTL)
    to_encode.update({"exp": expires})
    return jwt.encode(to_encode, JWT_SECRET, JWT_ALGORITHM)


async def create_token(session: AsyncSession, user: UserOut):
    access_token = create_access_token(data={"sub": str(user.id), "type": "access"})
    refresh_token_str = str(uuid.uuid4())
    expires_at = datetime.now(timezone.utc) + REFRESH_TOKEN_TTL
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


def decode_token(access_token: str) -> dict[str, Any]:
    try:
        return jwt.decode(access_token, JWT_SECRET, algorithms=JWT_ALGORITHM)
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def create_response_cookie(
    response: JSONResponse, tokens: dict[str, str]
) -> JSONResponse:
    response.set_cookie(
        key="access_token",
        value=tokens["access_token"],
        httponly=True,
        secure=True,
        samesite="Lax",
        max_age=int(ACCESS_TOKEN_TTL.total_seconds()),
    )
    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        secure=True,
        samesite="Lax",
        max_age=int(REFRESH_TOKEN_TTL.total_seconds()),
    )
    return response


def create_email_verification_token(user_id: int, token_type: str) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode = {"sub": str(user_id), "exp": expires_at, "type": token_type}
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_email_token_and_get_user(token: str, token_type: str) -> int:
    payload = decode_token(token)
    if not payload or payload.get("type") != token_type:
        return None
    return int(payload.get("sub"))


async def revoke_refresh_token(session: AsyncSession, refresh_token: str):
    stmt = select(RefreshToken).where(RefreshToken.tokens == refresh_token)
    result = await session.scalars(stmt)
    token = result.first()
    if token and token.expires_at > datetime.now(timezone.utc) and not token.revoked:
        token.revoked = True
        await session.commit()
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
