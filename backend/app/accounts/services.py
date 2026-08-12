from sqlalchemy.ext.asyncio import AsyncSession
from app.accounts.models import User
from app.accounts.schema import UserOut, UserCreate
from sqlalchemy import select
from fastapi import HTTPException, status

from app.accounts.utils import hash_password


async def user_create(session: AsyncSession, user: UserCreate):
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
