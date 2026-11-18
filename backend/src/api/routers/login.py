from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

import src.crud.user as user_crud
from src.api.deps import SessionWriterDep
from src.helper.config import settings
from src.helper.security import (
    create_access_token,
    get_password_hash,
    verify_password,
)
from src.models.user import User
from src.schemas.auth import Token, UserPublic, UserSignup

router = APIRouter()


@router.post(
    "/signup",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
    description="パスワード付きでユーザを登録する",
)
async def signup(body: UserSignup, db: SessionWriterDep) -> Any:
    if await user_crud.find_by_email(db, body.email, partial_match=False):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="このメールアドレスは登録済みです",
        )
    user = User(
        name=body.name,
        email=body.email,
        hashed_password=get_password_hash(body.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.post(
    "/login/access-token",
    response_model=Token,
    description="OAuth2 のパスワードフロー。username にメールアドレスを入れる",
)
async def login_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: SessionWriterDep
) -> Token:
    user = await user_crud.find_by_email(db, form_data.username, partial_match=False)
    # ユーザが居ない場合とパスワード違いを区別しない（どのメールアドレスが登録済みかを漏らさない）
    if (
        user is None
        or user.soft_destroyed_at is not None
        or user.hashed_password is None
        or not verify_password(form_data.password, user.hashed_password)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="メールアドレスかパスワードが違います",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(
        user.id, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return Token(access_token=token)
