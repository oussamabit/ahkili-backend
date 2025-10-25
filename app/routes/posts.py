from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app import crud, schemas, models
from app.database import get_db
from app.services.upload import delete_image , delete_video

router = APIRouter(prefix="/posts", tags=["posts"])

def check_post_delete_permission(post: models.Post, user_id: int, db: Session) -> bool:
    """
    Check if user can delete the post.
    Returns True if:
    - User owns the post
    - User is admin or moderator
    - User is moderator of the community the post belongs to
    """
    # Owner can always delete
    if post.user_id == user_id:
        return True
    
    # Get the user
    user = crud.get_user(db, user_id)
    if not user:
        return False
    
    # Admin and moderators can delete any post
    if user.role in ['admin', 'moderator']:
        return True
    
    # Community moderators can delete posts in their community
    if post.community_id:
        is_community_mod = db.query(models.CommunityModerator).filter(
            models.CommunityModerator.community_id == post.community_id,
            models.CommunityModerator.user_id == user_id
        ).first()
        if is_community_mod:
            return True
    
    return False

def serialize_post(post):
    """Helper function to serialize post with author info"""
    return {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "user_id": post.user_id,
        "community_id": post.community_id,
        "image_url": post.image_url,
        "video_url": post.video_url,
        "is_anonymous": post.is_anonymous if post.is_anonymous is not None else False,
        "created_at": post.created_at,
        "reactions_count": getattr(post, 'reactions_count', 0),
        "comments_count": getattr(post, 'comments_count', 0),
        "author": {
            "id": post.author.id,
            "username": post.author.username,
            "role": post.author.role,
            "verified": post.author.verified
        } if post.author else None,
        "community": {
            "id": post.community.id,
            "name": post.community.name
        } if post.community else None
    }

@router.get("/")
def get_posts(
    skip: int = 0,
    limit: int = 100,
    community_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    posts = crud.get_posts(db, skip=skip, limit=limit, community_id=community_id)
    return [serialize_post(post) for post in posts]

@router.get("/{post_id}")
def get_post(post_id: int, db: Session = Depends(get_db)):
    db_post = crud.get_post(db, post_id=post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return serialize_post(db_post)

@router.post("/")
def create_post(
    post: schemas.PostCreate,
    user_id: int,
    db: Session = Depends(get_db)
):
    created_post = crud.create_post(db=db, post=post, user_id=user_id)
    return serialize_post(created_post)

@router.delete("/{post_id}")
def delete_post(
    post_id: int, 
    user_id: int = Query(..., description="User ID attempting to delete"),
    reason: str = Query(None, description="Reason for deletion (required for admin/moderator)"),
    db: Session = Depends(get_db)
):
    # Get the post
    db_post = crud.get_post(db, post_id=post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Check permissions
    if not check_post_delete_permission(db_post, user_id, db):
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")
    
    # Get user to check if admin/moderator
    user = crud.get_user(db, user_id)
    
    # If admin/moderator deleting someone else's post, log it
    if user and user.role in ['admin', 'moderator'] and db_post.user_id != user_id:
        if not reason:
            raise HTTPException(status_code=400, detail="Reason required for admin/moderator deletion")
        
        # Log the moderation action
        crud.create_moderation_log(
            db,
            moderator_id=user_id,
            action='delete_post',
            target_type='post',
            target_id=post_id,
            reason=reason
        )
    
    # Delete post and get image_url
    # Delete post and get media URLs
    media_urls = crud.delete_post(db, post_id=post_id)
    
    # Delete media from Cloudinary if exists
    if media_urls:
        if media_urls.get('image_url'):
            delete_image(media_urls['image_url'])
        if media_urls.get('video_url'):
            delete_video(media_urls['video_url'])
    
    return {"message": "Post deleted successfully"}

@router.get("/user/{user_id}")
def get_user_posts(user_id: int, db: Session = Depends(get_db)):
    posts = crud.get_user_posts(db, user_id=user_id)
    return [serialize_post(post) for post in posts]

@router.get("/search")
def search_posts(
    q: str,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    posts = crud.search_posts(db, query=q, skip=skip, limit=limit)
    return [serialize_post(post) for post in posts]