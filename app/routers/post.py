from typing import List, Optional

from fastapi import Depends, APIRouter, HTTPException, Response, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..models import Like, Post
from ..oauth2 import get_current_user
from ..database import get_db
from ..schemas import PostCreate, PostResponse, PostOutput

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.get("/", response_model=List[PostOutput])
def get_posts(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    limit: int = 10,
    skip: int = 0,
    search: Optional[str] = "",
):

    posts = (
        db.query(Post, func.count(Like.post_id).label("likes"))
        .join(Like, Like.post_id == Post.id, isouter=True)
        .group_by(Post.id)
        .filter(Post.title.contains(search))
        .limit(limit)
        .offset(skip)
        .all()
    )
    return posts


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=PostResponse)
def create_post(
    post: PostCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user),
):

    new_post = Post(owner_id=current_user.id, **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


@router.get("/{id}", response_model=PostOutput)
def get_post(
    id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    post = (
        db.query(Post, func.count(Like.post_id).label("likes"))
        .join(Like, Like.post_id == Post.id, isouter=True)
        .group_by(Post.id)
        .first()
    )

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id {id} was not found",
        )
    return post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user),
):
    post_query = db.query(Post).filter(Post.id == id)
    post_to_delete = post_query.first()

    if not post_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id {id} was not found",
        )

    if post_to_delete.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to execute action",
        )

    post_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=PostResponse)
def update_post(
    id: int,
    post: PostCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user),
):
    post_query = db.query(Post).filter(Post.id == id)
    post_found = post_query.first()

    if not post_found:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id {id} was not found",
        )

    if post_found.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to execute action",
        )
    post_query.update(post.dict(), synchronize_session=False)
    db.commit()

    return post_query.first()
