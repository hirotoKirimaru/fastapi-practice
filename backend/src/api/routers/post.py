"""投稿の CRUD。full-stack-fastapi-template の items と同じく「自分のものだけ触れる、管理者は全部」"""

from typing import Annotated, Any

from fastapi import APIRouter, HTTPException, Query, status
from sqlmodel import col, select

from src.api.deps import SessionWriterDep
from src.auth.backend import CurrentUser
from src.models.post import Post
from src.models.user import User
from src.schemas.post import PostCreate, PostRead, PostUpdate

router = APIRouter()


async def _get_own_post(db: SessionWriterDep, post_id: int, user: User) -> Post:
    post = await db.get(Post, post_id)
    if post is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Post not found")
    if post.user_id != user.id and not user.is_superuser:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return post


@router.get(
    "", response_model=list[PostRead], description="自分の投稿（管理者は全員分）"
)
async def list_posts(
    db: SessionWriterDep,
    current_user: CurrentUser,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> Any:
    query = select(Post).order_by(col(Post.id)).offset(skip).limit(limit)
    if not current_user.is_superuser:
        query = query.where(Post.user_id == current_user.id)
    return (await db.execute(query)).scalars().all()


@router.post("", response_model=PostRead, status_code=status.HTTP_201_CREATED)
async def create_post(
    body: PostCreate, db: SessionWriterDep, current_user: CurrentUser
) -> Any:
    assert current_user.id is not None
    post = Post(title=body.title, user_id=current_user.id)
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return post


@router.get("/{post_id}", response_model=PostRead)
async def read_post(
    post_id: int, db: SessionWriterDep, current_user: CurrentUser
) -> Any:
    return await _get_own_post(db, post_id, current_user)


@router.patch("/{post_id}", response_model=PostRead)
async def update_post(
    post_id: int, body: PostUpdate, db: SessionWriterDep, current_user: CurrentUser
) -> Any:
    post = await _get_own_post(db, post_id, current_user)
    post.title = body.title
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int, db: SessionWriterDep, current_user: CurrentUser
) -> None:
    post = await _get_own_post(db, post_id, current_user)
    await db.delete(post)
    await db.commit()
