from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from app.accounts.schema import UserCreate, UserOut, UserLogin
from app.db.config import SessionDep
from app.accounts.services import user_create, authenticate_user, verify_refresh_token
from app.accounts.utils import create_response_cookie, create_token
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


@router.post("/refresh")
async def refresh_token(session: SessionDep, request: Request):
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Refresh Token"
        )
    user = await verify_refresh_token(session, refresh_token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    tokens = await create_token(session, user)
    response = JSONResponse({"message": "Token refreshed"})
    return create_response_cookie(response, tokens)
