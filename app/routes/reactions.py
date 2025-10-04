from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud
from app.database import get_db

router = APIRouter(prefix="/reactions", tags=["reactions"])

@router.post("/post/{post_id}")
def toggle_reaction(
    post_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    # Check if post exists
    post = crud.get_post(db, post_id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Toggle reaction
    reaction = crud.add_reaction(db, post_id=post_id, user_id=user_id)
    
    # Get updated count
    count = crud.get_post_reactions_count(db, post_id=post_id)
    has_reacted = crud.has_user_reacted(db, post_id=post_id, user_id=user_id)
    
    return {
        "success": True,
        "reactions_count": count,
        "user_has_reacted": has_reacted
    }

@router.get("/post/{post_id}/count")
def get_reactions_count(post_id: int, db: Session = Depends(get_db)):
    count = crud.get_post_reactions_count(db, post_id=post_id)
    return {"count": count}

@router.get("/post/{post_id}/user/{user_id}")
def check_user_reaction(post_id: int, user_id: int, db: Session = Depends(get_db)):
    has_reacted = crud.has_user_reacted(db, post_id=post_id, user_id=user_id)
    return {"has_reacted": has_reacted}