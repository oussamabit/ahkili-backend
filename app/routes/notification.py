
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/notification", tags=["notification"])

# ============= NOTIFICATION PREFERENCE ROUTES =============
@router.get("/notification-preferences/{user_id}", response_model=schemas.NotificationPreferenceResponse)
def get_notification_preferences(user_id: int, db: Session = Depends(get_db)):
    """Get user's notification preferences"""
    prefs = crud.get_or_create_notification_preferences(db, user_id)
    return prefs

@router.put("/notification-preferences/{user_id}", response_model=schemas.NotificationPreferenceResponse)
def update_notification_preferences(
    user_id: int,
    preferences: schemas.NotificationPreferenceCreate,
    db: Session = Depends(get_db)
):
    """Update user's notification preferences"""
    prefs = crud.update_notification_preferences(db, user_id, preferences.dict())
    return prefs


# ============= NOTIFICATION ROUTES =============
@router.get("/notifications/{user_id}", response_model=List[schemas.NotificationResponse])
def get_user_notifications(
    user_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get user's notifications"""
    notifications = crud.get_user_notifications(db, user_id, skip, limit)
    return notifications

@router.get("/notifications/{user_id}/unread/count")
def get_unread_notifications_count(user_id: int, db: Session = Depends(get_db)):
    """Get count of unread notifications"""
    count = crud.get_unread_notifications_count(db, user_id)
    return {"count": count}

@router.put("/notifications/{notification_id}/read")
def mark_notification_read(
    notification_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Mark a notification as read"""
    success = crud.mark_notification_as_read(db, notification_id, user_id)
    if success:
        return {"message": "Notification marked as read"}
    raise HTTPException(status_code=404, detail="Notification not found")

@router.put("/notifications/{user_id}/read-all")
def mark_all_notifications_read(user_id: int, db: Session = Depends(get_db)):
    """Mark all user's notifications as read"""
    crud.mark_all_notifications_as_read(db, user_id)
    return {"message": "All notifications marked as read"}

@router.delete("/notifications/{notification_id}")
def delete_notification(
    notification_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Delete a notification"""
    success = crud.delete_notification(db, notification_id, user_id)
    if success:
        return {"message": "Notification deleted"}
    raise HTTPException(status_code=404, detail="Notification not found")


# ============= COMMUNITY FOLLOWER ROUTES =============
@router.post("/communities/{community_id}/follow", response_model=schemas.CommunityFollowerResponse)
def follow_community(
    community_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Follow a community"""
    follower = crud.follow_community(db, community_id, user_id)
    return follower

@router.delete("/communities/{community_id}/follow")
def unfollow_community(
    community_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Unfollow a community"""
    success = crud.unfollow_community(db, community_id, user_id)
    if success:
        return {"message": "Unfollowed community"}
    raise HTTPException(status_code=404, detail="Not following this community")

@router.get("/communities/{community_id}/follow/check")
def check_following_community(
    community_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Check if user is following a community"""
    is_following = crud.is_following_community(db, community_id, user_id)
    return {"is_following": is_following}

@router.get("/communities/{community_id}/followers")
def get_community_followers(community_id: int, db: Session = Depends(get_db)):
    """Get all followers of a community"""
    followers = crud.get_community_followers(db, community_id)
    return {"count": len(followers), "followers": followers}