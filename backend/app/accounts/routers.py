from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse
from app.accounts.schema import UserCreate, UserOut, UserLogin, ChangePassword
from app.db.config import SessionDep
from app.accounts.services import (
    change_user_password,
    email_verification_send,
    email_verify,
    user_create,
    authenticate_user,
    verify_email_token,
    verify_refresh_token,
)
from app.accounts.utils import create_response_cookie, create_token
from app.accounts.dependencies import get_current_user
from app.accounts.models import User

router = APIRouter()


@router.post("/register")
async def create_user(session: SessionDep, user: UserCreate):
    return await user_create(session, user)


@router.post("/login")
async def login(session: SessionDep, user: UserLogin) -> JSONResponse:
    user = await authenticate_user(session, user)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credential")
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


@router.post("/send-verification-email")
async def send_verification_email(session: SessionDep, email: str):
    user = await email_verify(session, email)
    return await email_verification_send(user)


@router.get("/verify-email")
async def verify_email(session: SessionDep, token: Annotated[str, Query()]):
    return await verify_email_token(session, token)


@router.post("/change-password")
async def change_password(
    session: SessionDep,
    password: ChangePassword,
    user: User = Depends(get_current_user),
):
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credential")
    return await change_user_password(session, password, user)
