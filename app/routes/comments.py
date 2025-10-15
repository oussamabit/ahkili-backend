from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/comments", tags=["comments"])

@router.get("/post/{post_id}")
def get_comments(post_id: int, db: Session = Depends(get_db)):
    """Get all comments and replies for a post"""
    # Check if post exists
    post = crud.get_post(db, post_id=post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Get comments with replies
    comments = crud.get_comments_with_replies(db, post_id=post_id)
    
    # Add reaction counts to each comment
    result = []
    for comment in comments:
        comment_dict = {
            "id": comment.id,
            "content": comment.content,
            "user_id": comment.user_id,
            "post_id": comment.post_id,
            "parent_id": comment.parent_id,
            "created_at": comment.created_at,
            "author": {
                "id": comment.author.id,
                "username": comment.author.username,
                "role": comment.author.role,
                "verified": comment.author.verified
            },
            "reactions": crud.get_comment_reactions_count(db, comment.id),
            "replies": []
        }
        
        # Add replies with their reactions
        for reply in comment.replies:
            reply_dict = {
                "id": reply.id,
                "content": reply.content,
                "user_id": reply.user_id,
                "post_id": reply.post_id,
                "parent_id": reply.parent_id,
                "created_at": reply.created_at,
                "author": {
                    "id": reply.author.id,
                    "username": reply.author.username,
                    "role": reply.author.role,
                    "verified": reply.author.verified
                },
                "reactions": crud.get_comment_reactions_count(db, reply.id)
            }
            comment_dict["replies"].append(reply_dict)
        
        result.append(comment_dict)
    
    return result

@router.post("/post/{post_id}")
def create_comment(
    post_id: int,
    comment: schemas.CommentCreate,
    user_id: int,
    parent_id: Optional[int] = None,  # For replies
    db: Session = Depends(get_db)
):
    """Create a comment or reply"""
    # Check if post exists
    post = crud.get_post(db, post_id=post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # If it's a reply, check if parent comment exists
    if parent_id:
        parent_comment = db.query(crud.models.Comment).filter(
            crud.models.Comment.id == parent_id
        ).first()
        if not parent_comment:
            raise HTTPException(status_code=404, detail="Parent comment not found")
    
    # Create comment with parent_id
    db_comment = crud.models.Comment(
        content=comment.content,
        post_id=post_id,
        user_id=user_id,
        parent_id=parent_id
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    
    return {
        "id": db_comment.id,
        "content": db_comment.content,
        "user_id": db_comment.user_id,
        "post_id": db_comment.post_id,
        "parent_id": db_comment.parent_id,
        "created_at": db_comment.created_at,
        "author": {
            "id": db_comment.author.id,
            "username": db_comment.author.username,
            "role": db_comment.author.role,
            "verified": db_comment.author.verified
        },
        "reactions": {"likes": 0, "dislikes": 0}
    }