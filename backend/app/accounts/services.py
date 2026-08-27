from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from app.accounts.models import User, RefreshToken
from app.accounts.schema import UserCreate
from sqlalchemy import select
from fastapi import HTTPException, status

from app.accounts.utils import hash_password, verify_password, create_access_token


async def user_create(session: AsyncSession, user: UserCreate) -> User:
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
    return new_user


async def login_user(session: AsyncSession, username: str, password: str) -> str:
    if not username or not password:
        raise HTTPException("Username and password should be provided")
    stmt = select(User).where(User.email == username)
    result = await session.scalar(stmt)
    if not result:
        return HTTPException("User not found")
    print(password, result.hashed_password)
    if not verify_password(password, result.hashed_password):
        return HTTPException("Password did not match")
    access_token = create_access_token(data={"sub": str(result.id)})
    return access_token


async def authenticate_user(session: AsyncSession, user: User) -> User:
    if user.email is None or user.password is None:
        raise HTTPException("Email and password should be provided")
    stmt = select(User).where(User.email == user.email)
    result = await session.scalars(stmt)
    user = result.first()
    if not user and not verify_password(user.password, user.hashed_password):
        return None
    return user


async def verify_refresh_token(session: AsyncSession, refresh_token: str) -> User | None:
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
            return user_result.first()
    return None
