from fastapi import APIRouter
from app.accounts.schema import UserCreate, UserOut
from app.db.config import SessionDep
from app.accounts.services import user_create

router = APIRouter()


@router.post("/register", response_model=UserOut)
async def create_user(session: SessionDep, user: UserCreate) -> UserOut:
    return await user_create(session, user)
