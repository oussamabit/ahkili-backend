from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud
from app.database import get_db

router = APIRouter(prefix="/comment-reactions", tags=["comment-reactions"])

@router.post("/comment/{comment_id}")
def toggle_comment_reaction(
    comment_id: int,
    user_id: int,
    reaction_type: str = "like",  # 'like' or 'dislike'
    db: Session = Depends(get_db)
):
    """Toggle like/dislike on a comment"""
    if reaction_type not in ['like', 'dislike']:
        raise HTTPException(status_code=400, detail="reaction_type must be 'like' or 'dislike'")
    
    # Toggle reaction
    crud.toggle_comment_reaction(db, comment_id=comment_id, user_id=user_id, reaction_type=reaction_type)
    
    # Get updated counts
    counts = crud.get_comment_reactions_count(db, comment_id=comment_id)
    user_reaction = crud.get_user_comment_reaction(db, comment_id=comment_id, user_id=user_id)
    
    return {
        "success": True,
        "likes": counts["likes"],
        "dislikes": counts["dislikes"],
        "user_reaction": user_reaction
    }

@router.get("/comment/{comment_id}")
def get_comment_reactions(
    comment_id: int,
    user_id: int = None,
    db: Session = Depends(get_db)
):
    """Get reaction counts for a comment"""
    counts = crud.get_comment_reactions_count(db, comment_id=comment_id)
    user_reaction = None
    
    if user_id:
        user_reaction = crud.get_user_comment_reaction(db, comment_id=comment_id, user_id=user_id)
    
    return {
        "likes": counts["likes"],
        "dislikes": counts["dislikes"],
        "user_reaction": user_reaction
    }