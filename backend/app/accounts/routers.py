from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from app.accounts.schema import UserCreate, UserOut, UserLogin
from app.db.config import SessionDep
from app.accounts.services import user_create, authenticate_user
from app.accounts.utils import create_token
from app.accounts.dependencies import get_current_user
from app.accounts.models import User

router = APIRouter()


@router.post("/register", response_model=UserOut)
async def create_user(session: SessionDep, user: UserCreate) -> UserOut:
    return await user_create(session, user)


@router.post("/login")
async def login(session: SessionDep, user: UserLogin) -> JSONResponse:
    user = await authenticate_user(session, user)
    if not user:
        return HTTPException(status_code=401, detail="Invalid credential")
    tokens = await create_token(session, user)
    response = JSONResponse(content={"data": "Login Success"})
    response.set_cookie(
        key="access_token",
        value=tokens["access_token"],
        httponly=True,
        secure=True,
        samesite="Lax",
        max_age=60 * 60 * 21 * 1,
    )
    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        secure=True,
        samesite="Lax",
        max_age=60 * 60 * 21 * 1,
    )
    return response


@router.get("/me", response_model=UserOut)
async def me(user: User = Depends(get_current_user)) -> UserOut:
    return user
