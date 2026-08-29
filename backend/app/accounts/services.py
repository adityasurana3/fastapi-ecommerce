from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from app.accounts.models import User, RefreshToken
from app.accounts.schema import UserCreate, UserLogin
from sqlalchemy import select
from fastapi import HTTPException, status

from app.accounts.utils import (
    create_email_verification_token,
    hash_password,
    verify_email_token_and_get_user,
    verify_password,
    create_access_token,
)


async def user_create(session: AsyncSession, user: UserCreate) -> dict[str, str]:
    stmt = select(User).where(User.email == user.email)
    result = await session.scalars(stmt)
    if result.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User already exist"
        )
    new_user = User(email=user.email, hashed_password=hash_password(user.password))
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return await email_verification_send(new_user)


async def authenticate_user(session: AsyncSession, user: UserLogin) -> User | None:
    if user.email is None or user.password is None:
        raise HTTPException("Email and password should be provided")
    stmt = select(User).where(User.email == user.email)
    result = await session.scalars(stmt)
    db_user = result.first()
    if not db_user:
        return None
    if not verify_password(user.password, db_user.hashed_password):
        return None
    if not db_user.is_active:
        return None
    if not db_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Email not verified"
        )
    return db_user


async def verify_refresh_token(
    session: AsyncSession, refresh_token: str
) -> User | None:
    stmt = select(RefreshToken).where(RefreshToken.tokens == refresh_token)
    result = await session.scalars(stmt)
    token = result.first()
    if token and not token.revoked:
        expires_at = token.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at > datetime.now(timezone.utc):
            user_stmt = select(User).where(User.id == token.user_id)
            user_result = await session.scalars(user_stmt)
            user = user_result.first()
            if not user or not user.is_active:
                return None
            return user
    return None


async def email_verification_send(user: User) -> dict[str, str]:
    token = create_email_verification_token(user.id)
    link = f"http://127.0.0.1:8000/api/account/verify-email?token={token}"
    print("Email verification token", link)
    return {"msg": "Verification email sent"}


async def verify_email_token(session: AsyncSession, token: str):
    user_id = verify_email_token_and_get_user(token, "verify_email")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token"
        )
    stmt = select(User).where(User.id == user_id)
    result = await session.scalars(stmt)
    user = result.first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    user.is_verified = True
    session.add(user)
    await session.commit()
    return {"msg": "Email successfully verified"}


async def email_verify(session: AsyncSession, email: str) -> User:
    stmt = select(User).where(User.email == email)
    result = await session.scalars(stmt)
    user = result.first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user
