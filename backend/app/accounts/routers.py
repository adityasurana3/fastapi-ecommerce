from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from app.accounts.schema import UserCreate, UserOut
from app.db.config import SessionDep
from app.accounts.services import user_create, authenticate_user
from fastapi.security import OAuth2PasswordRequestForm
from app.accounts.utils import create_token

router = APIRouter()


@router.post("/register", response_model=UserOut)
async def create_user(session: SessionDep, user: UserCreate) -> UserOut:
    return await user_create(session, user)


@router.post("/login")
async def login(session: SessionDep, form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(session, form_data.username, form_data.password)
    if not user:
        return HTTPException(status_code=401, detail="Invalid credential")
    tokens = await create_token(session, user)
    response = JSONResponse({"access_token": tokens["access_token"]})
    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        secure=True,
        samesite="Lax",
    )
    return response
