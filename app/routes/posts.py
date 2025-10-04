from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/posts", tags=["posts"])

@router.get("/", response_model=List[schemas.PostResponse])
def get_posts(
    skip: int = 0,
    limit: int = 100,
    community_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    posts = crud.get_posts(db, skip=skip, limit=limit, community_id=community_id)
    return posts

@router.get("/{post_id}", response_model=schemas.PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    db_post = crud.get_post(db, post_id=post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return db_post

@router.post("/", response_model=schemas.PostResponse)
def create_post(
    post: schemas.PostCreate,
    user_id: int,
    db: Session = Depends(get_db)
):
    return crud.create_post(db=db, post=post, user_id=user_id)

@router.delete("/{post_id}")
def delete_post(post_id: int, user_id: int, db: Session = Depends(get_db)):
    # Get the post
    db_post = crud.get_post(db, post_id=post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Check if user owns the post
    if db_post.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")
    
    crud.delete_post(db, post_id=post_id)
    return {"message": "Post deleted successfully"}

@router.get("/user/{user_id}", response_model=List[schemas.PostResponse])
def get_user_posts(user_id: int, db: Session = Depends(get_db)):
    from app import crud as crud_ops
    return crud_ops.get_user_posts(db, user_id=user_id)

@router.get("/search", response_model=List[schemas.PostResponse])
def search_posts(
    q: str,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    from app import crud as crud_ops
    return crud_ops.search_posts(db, query=q, skip=skip, limit=limit)