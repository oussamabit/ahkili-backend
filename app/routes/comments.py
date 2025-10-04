from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/comments", tags=["comments"])

@router.get("/post/{post_id}", response_model=List[schemas.CommentResponse])
def get_comments(post_id: int, db: Session = Depends(get_db)):
    # Check if post exists
    post = crud.get_post(db, post_id=post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return crud.get_comments(db, post_id=post_id)

@router.post("/post/{post_id}", response_model=schemas.CommentResponse)
def create_comment(
    post_id: int,
    comment: schemas.CommentCreate,
    user_id: int,
    db: Session = Depends(get_db)
):
    # Check if post exists
    post = crud.get_post(db, post_id=post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return crud.create_comment(db=db, comment=comment, post_id=post_id, user_id=user_id)