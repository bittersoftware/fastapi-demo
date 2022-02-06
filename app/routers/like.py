from fastapi import APIRouter, Depends, FastAPI, HTTPException, Response, status
from sqlalchemy.orm import Session
from starlette.status import HTTP_404_NOT_FOUND

from ..database import get_db
from ..models import Like, Post
from ..oauth2 import get_current_user
from ..schemas import LikeResponse

router = APIRouter(prefix="/like", tags=["Like"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def like(
    like: LikeResponse,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user),
):
    post = db.query(Post).filter(Post.id == like.post_id).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id {like.post_id} does not exist",
        )

    like_query = db.query(Like).filter(
        Like.post_id == like.post_id, Like.user_id == current_user.id
    )

    found_like = like_query.first()

    if like.direction is True:
        if found_like:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"user {current_user.id} has already like on post {like.post_id}",
            )

        new_like = Like(post_id=like.post_id, user_id=current_user.id)
        db.add(new_like)
        db.commit()
        return {"message": "successfully added like"}

    else:
        if not found_like:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND, detail="Like does not exist"
            )
        like_query.delete(synchronize_session=False)
        db.commit()

        return {"message": "successfully deleted like"}
