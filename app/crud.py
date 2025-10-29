from sqlalchemy.orm import Session
from app import models, schemas
from typing import List, Optional
from datetime import datetime

# ============= USER CRUD =============
def get_user_by_firebase_uid(db: Session, firebase_uid: str):
    return db.query(models.User).filter(models.User.firebase_uid == firebase_uid).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        firebase_uid=user.firebase_uid,
        username=user.username,
        email=user.email
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

# Add after get_user function
def update_user_profile(db: Session, user_id: int, updates: dict):
    """Update user profile information"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return None
    
    # Update only provided fields
    for key, value in updates.items():
        if value is not None and hasattr(user, key):
            setattr(user, key, value)
    
    db.commit()
    db.refresh(user)
    return user

def get_user_profile_stats(db: Session, user_id: int):
    """Get user profile statistics"""
    posts_count = db.query(models.Post).filter(models.Post.user_id == user_id).count()
    
    # Count communities where user is a member
    communities_count = db.query(models.CommunityMember).filter(
        models.CommunityMember.user_id == user_id
    ).count()
    
    return {
        "posts_count": posts_count,
        "communities_count": communities_count
    }

# ============= COMMUNITY CRUD =============
def get_communities(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Community).offset(skip).limit(limit).all()

def get_community(db: Session, community_id: int):
    return db.query(models.Community).filter(models.Community.id == community_id).first()

def create_community(db: Session, name: str, description: str, created_by: int):
    db_community = models.Community(
        name=name,
        description=description,
        created_by=created_by
    )
    db.add(db_community)
    db.commit()
    db.refresh(db_community)
    return db_community

# ============= POST CRUD =============
def get_posts(db: Session, skip: int = 0, limit: int = 100, community_id: Optional[int] = None):
    query = db.query(models.Post)
    if community_id:
        query = query.filter(models.Post.community_id == community_id)
    posts = query.order_by(models.Post.created_at.desc()).offset(skip).limit(limit).all()
    
    # Add reactions and comments count to each post
    for post in posts:
        post.reactions_count = get_post_reactions_count(db, post.id)
        post.comments_count = db.query(models.Comment).filter(models.Comment.post_id == post.id).count()
        if post.is_anonymous is None:
            post.is_anonymous = False
    return posts

def get_post(db: Session, post_id: int):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post:
        # Add reactions count
        post.reactions_count = get_post_reactions_count(db, post_id)
        # Add comments count
        post.comments_count = db.query(models.Comment).filter(models.Comment.post_id == post_id).count()
        if post.is_anonymous is None:
            post.is_anonymous = False
    return post

def create_post(db: Session, post: schemas.PostCreate, user_id: int):
    db_post = models.Post(
        title=post.title,
        content=post.content,
        community_id=post.community_id,
        user_id=user_id,
        image_url=post.image_url,
        video_url=post.video_url,
        is_anonymous=post.is_anonymous
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

def delete_post(db: Session, post_id: int):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post:
        # Store media URLs before deleting
        media_urls = {
            'image_url': post.image_url,
            'video_url': post.video_url
        }
        
        # Delete post from database
        db.delete(post)
        db.commit()
        
        # Return media URLs so we can delete them from Cloudinary
        return media_urls
    return None

# ============= COMMENT CRUD =============
def get_comments(db: Session, post_id: int):
    return db.query(models.Comment).filter(models.Comment.post_id == post_id).order_by(models.Comment.created_at.asc()).all()

def create_comment(db: Session, comment: schemas.CommentCreate, post_id: int, user_id: int):
    db_comment = models.Comment(
        content=comment.content,
        post_id=post_id,
        user_id=user_id
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

# ============= HOTLINE CRUD =============
def get_hotlines(db: Session, country: Optional[str] = None):
    query = db.query(models.Hotline)
    if country:
        query = query.filter(models.Hotline.country == country)
    return query.all()

def get_user_posts(db: Session, user_id: int):
    posts = db.query(models.Post).filter(models.Post.user_id == user_id).order_by(models.Post.created_at.desc()).all()
    
    # Add reactions and comments count to each post
    for post in posts:
        post.reactions_count = get_post_reactions_count(db, post.id)
        post.comments_count = db.query(models.Comment).filter(models.Comment.post_id == post.id).count()
        if post.is_anonymous is None:
            post.is_anonymous = False
    return posts

# ============= SEARCH FUNCTIONS =============
def search_posts(db: Session, query: str, skip: int = 0, limit: int = 50):
    posts = db.query(models.Post).filter(
        models.Post.title.ilike(f'%{query}%') | models.Post.content.ilike(f'%{query}%')
    ).order_by(models.Post.created_at.desc()).offset(skip).limit(limit).all()
    
    # Add reactions and comments count to each post
    for post in posts:
        post.reactions_count = get_post_reactions_count(db, post.id)
        post.comments_count = db.query(models.Comment).filter(models.Comment.post_id == post.id).count()
        if post.is_anonymous is None:
            post.is_anonymous = False
    return posts

def search_communities(db: Session, query: str):
    return db.query(models.Community).filter(
        models.Community.name.ilike(f'%{query}%') | models.Community.description.ilike(f'%{query}%')
    ).all()

# ============= REACTION CRUD =============
def add_reaction(db: Session, post_id: int, user_id: int, reaction_type: str = "like"):
    # Check if reaction already exists
    existing = db.query(models.PostReaction).filter(
        models.PostReaction.post_id == post_id,
        models.PostReaction.user_id == user_id
    ).first()
    
    if existing:
        # Remove reaction (unlike)
        db.delete(existing)
        db.commit()
        return None
    else:
        # Add new reaction
        reaction = models.PostReaction(
            post_id=post_id,
            user_id=user_id,
            reaction_type=reaction_type
        )
        db.add(reaction)
        db.commit()
        db.refresh(reaction)
        return reaction

def get_post_reactions_count(db: Session, post_id: int):
    return db.query(models.PostReaction).filter(models.PostReaction.post_id == post_id).count()

def has_user_reacted(db: Session, post_id: int, user_id: int):
    reaction = db.query(models.PostReaction).filter(
        models.PostReaction.post_id == post_id,
        models.PostReaction.user_id == user_id
    ).first()
    return reaction is not None


# ============= ADMIN/MODERATOR FUNCTIONS =============
def promote_user(db: Session, user_id: int, role: str):
    """Promote user to moderator or admin"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        user.role = role
        db.commit()
        db.refresh(user)
        return user
    return None

def get_all_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def ban_user(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        user.role = 'banned'
        db.commit()
        return True
    return False

# ============= REPORT CRUD =============
def create_report(db: Session, reported_by: int, target_type: str, target_id: int, reason: str):
    report = models.Report(
        reported_by=reported_by,
        target_type=target_type,
        target_id=target_id,
        reason=reason
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report

def get_reports(db: Session, status: str = None):
    query = db.query(models.Report)
    if status:
        query = query.filter(models.Report.status == status)
    return query.order_by(models.Report.created_at.desc()).all()

def resolve_report(db: Session, report_id: int, resolved_by: int):
    report = db.query(models.Report).filter(models.Report.id == report_id).first()
    if report:
        report.status = 'resolved'
        report.resolved_by = resolved_by
        report.resolved_at = datetime.utcnow()
        db.commit()
        return True
    return False

# ============= MODERATION LOG =============
def create_moderation_log(db: Session, moderator_id: int, action: str, target_type: str, target_id: int, reason: str):
    log = models.ModerationLog(
        moderator_id=moderator_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        reason=reason
    )
    db.add(log)
    db.commit()
    return log

# ============= DOCTOR VERIFICATION =============
def submit_doctor_verification(
    db: Session,
    user_id: int,
    full_name: str,
    specialization: str,
    license_number: str,
    license_document_url: str,
    clinic_address: str,
    phone_number: str,
    bio: str
):
    verification = models.DoctorVerification(
        user_id=user_id,
        full_name=full_name,
        specialization=specialization,
        license_number=license_number,
        license_document_url=license_document_url,
        clinic_address=clinic_address,
        phone_number=phone_number,
        bio=bio
    )
    db.add(verification)
    db.commit()
    db.refresh(verification)
    return verification

def get_pending_verifications(db: Session):
    return db.query(models.DoctorVerification).filter(
        models.DoctorVerification.status == 'pending'
    ).order_by(models.DoctorVerification.submitted_at.desc()).all()

def get_all_verifications(db: Session):
    return db.query(models.DoctorVerification).order_by(
        models.DoctorVerification.submitted_at.desc()
    ).all()

def approve_doctor_verification(db: Session, verification_id: int, admin_id: int):
    verification = db.query(models.DoctorVerification).filter(
        models.DoctorVerification.id == verification_id
    ).first()
    
    if not verification:
        return None
    
    # Update verification status
    verification.status = 'approved'
    verification.reviewed_by = admin_id
    verification.reviewed_at = datetime.utcnow()
    
    # Update user role to doctor
    user = db.query(models.User).filter(models.User.id == verification.user_id).first()
    if user:
        user.role = 'doctor'
        user.verified = True
    
    db.commit()
    db.refresh(verification)
    return verification

def reject_doctor_verification(db: Session, verification_id: int, admin_id: int, reason: str):
    verification = db.query(models.DoctorVerification).filter(
        models.DoctorVerification.id == verification_id
    ).first()
    
    if not verification:
        return None
    
    verification.status = 'rejected'
    verification.reviewed_by = admin_id
    verification.reviewed_at = datetime.utcnow()
    verification.rejection_reason = reason
    
    db.commit()
    db.refresh(verification)
    return verification

def get_user_verification(db: Session, user_id: int):
    return db.query(models.DoctorVerification).filter(
        models.DoctorVerification.user_id == user_id
    ).first()

# ============= COMMUNITY MODERATORS =============
def assign_community_moderator(db: Session, community_id: int, user_id: int, assigned_by: int):
    moderator = models.CommunityModerator(
        community_id=community_id,
        user_id=user_id,
        assigned_by=assigned_by
    )
    db.add(moderator)
    db.commit()
    db.refresh(moderator)
    return moderator

def remove_community_moderator(db: Session, community_id: int, user_id: int):
    moderator = db.query(models.CommunityModerator).filter(
        models.CommunityModerator.community_id == community_id,
        models.CommunityModerator.user_id == user_id
    ).first()
    
    if moderator:
        db.delete(moderator)
        db.commit()
        return True
    return False

def get_community_moderators(db: Session, community_id: int):
    return db.query(models.CommunityModerator).filter(
        models.CommunityModerator.community_id == community_id
    ).all()

def is_community_moderator(db: Session, community_id: int, user_id: int):
    moderator = db.query(models.CommunityModerator).filter(
        models.CommunityModerator.community_id == community_id,
        models.CommunityModerator.user_id == user_id
    ).first()
    return moderator is not None

def get_user_moderated_communities(db: Session, user_id: int):
    return db.query(models.CommunityModerator).filter(
        models.CommunityModerator.user_id == user_id
    ).all()


# ============= COMMENT REACTION CRUD =============
def toggle_comment_reaction(db: Session, comment_id: int, user_id: int, reaction_type: str = "like"):
    """Toggle like/dislike on a comment"""
    # Check if reaction already exists
    existing = db.query(models.CommentReaction).filter(
        models.CommentReaction.comment_id == comment_id,
        models.CommentReaction.user_id == user_id
    ).first()
    
    if existing:
        if existing.reaction_type == reaction_type:
            # Remove reaction (unlike/undislike)
            db.delete(existing)
            db.commit()
            return None
        else:
            # Change reaction type (like to dislike or vice versa)
            existing.reaction_type = reaction_type
            db.commit()
            db.refresh(existing)
            return existing
    else:
        # Add new reaction
        reaction = models.CommentReaction(
            comment_id=comment_id,
            user_id=user_id,
            reaction_type=reaction_type
        )
        db.add(reaction)
        db.commit()
        db.refresh(reaction)
        return reaction

def get_comment_reactions_count(db: Session, comment_id: int):
    """Get like and dislike counts for a comment"""
    likes = db.query(models.CommentReaction).filter(
        models.CommentReaction.comment_id == comment_id,
        models.CommentReaction.reaction_type == "like"
    ).count()
    
    dislikes = db.query(models.CommentReaction).filter(
        models.CommentReaction.comment_id == comment_id,
        models.CommentReaction.reaction_type == "dislike"
    ).count()
    
    return {"likes": likes, "dislikes": dislikes}

def get_user_comment_reaction(db: Session, comment_id: int, user_id: int):
    """Get user's reaction on a comment"""
    reaction = db.query(models.CommentReaction).filter(
        models.CommentReaction.comment_id == comment_id,
        models.CommentReaction.user_id == user_id
    ).first()
    
    return reaction.reaction_type if reaction else None

# Update get_comments to include nested replies
def get_comments_with_replies(db: Session, post_id: int):
    """Get comments with their replies and reaction counts"""
    # Get all comments for the post
    all_comments = db.query(models.Comment).filter(
        models.Comment.post_id == post_id
    ).order_by(models.Comment.created_at.asc()).all()
    
    # Separate parent comments and replies
    parent_comments = [c for c in all_comments if c.parent_id is None]
    
    # Build comment tree
    for comment in parent_comments:
        comment.replies = [c for c in all_comments if c.parent_id == comment.id]
    
    return parent_comments

# ============= NOTIFICATION PREFERENCE CRUD =============
def get_or_create_notification_preferences(db: Session, user_id: int):
    """Get user's notification preferences or create default ones"""
    prefs = db.query(models.NotificationPreference).filter(
        models.NotificationPreference.user_id == user_id
    ).first()
    
    if not prefs:
        prefs = models.NotificationPreference(user_id=user_id)
        db.add(prefs)
        db.commit()
        db.refresh(prefs)
    
    return prefs


def update_notification_preferences(db: Session, user_id: int, preferences: dict):
    """Update user's notification preferences"""
    prefs = get_or_create_notification_preferences(db, user_id)
    
    for key, value in preferences.items():
        if hasattr(prefs, key):
            setattr(prefs, key, value)
    
    prefs.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(prefs)
    return prefs


# ============= NOTIFICATION CRUD =============
def create_notification(
    db: Session,
    user_id: int,
    notification_type: str,
    title: str,
    message: str,
    target_type: str = None,
    target_id: int = None,
    actor_id: int = None
):
    """Create a new notification"""
    # Check if user has this notification type enabled
    prefs = get_or_create_notification_preferences(db, user_id)
    
    # Map notification types to preference fields
    pref_mapping = {
        'comment_reaction': prefs.comment_reactions,
        'comment_reply': prefs.comment_replies,
        'post_reaction': prefs.post_reactions,
        'new_post': prefs.new_posts
    }
    
    # Only create notification if user has enabled this type
    if not pref_mapping.get(notification_type, True):
        return None
    
    notification = models.Notification(
        user_id=user_id,
        type=notification_type,
        title=title,
        message=message,
        target_type=target_type,
        target_id=target_id,
        actor_id=actor_id
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def get_user_notifications(db: Session, user_id: int, skip: int = 0, limit: int = 50):
    """Get user's notifications"""
    return db.query(models.Notification).filter(
        models.Notification.user_id == user_id
    ).order_by(models.Notification.created_at.desc()).offset(skip).limit(limit).all()


def get_unread_notifications_count(db: Session, user_id: int):
    """Get count of unread notifications"""
    return db.query(models.Notification).filter(
        models.Notification.user_id == user_id,
        models.Notification.is_read == False
    ).count()


def mark_notification_as_read(db: Session, notification_id: int, user_id: int):
    """Mark a notification as read"""
    notification = db.query(models.Notification).filter(
        models.Notification.id == notification_id,
        models.Notification.user_id == user_id
    ).first()
    
    if notification:
        notification.is_read = True
        db.commit()
        return True
    return False


def mark_all_notifications_as_read(db: Session, user_id: int):
    """Mark all user's notifications as read"""
    db.query(models.Notification).filter(
        models.Notification.user_id == user_id,
        models.Notification.is_read == False
    ).update({"is_read": True})
    db.commit()
    return True


def delete_notification(db: Session, notification_id: int, user_id: int):
    """Delete a notification"""
    notification = db.query(models.Notification).filter(
        models.Notification.id == notification_id,
        models.Notification.user_id == user_id
    ).first()
    
    if notification:
        db.delete(notification)
        db.commit()
        return True
    return False


# ============= COMMUNITY FOLLOWER CRUD =============
def follow_community(db: Session, community_id: int, user_id: int):
    """Follow a community"""
    existing = db.query(models.CommunityFollower).filter(
        models.CommunityFollower.community_id == community_id,
        models.CommunityFollower.user_id == user_id
    ).first()
    
    if existing:
        return existing
    
    follower = models.CommunityFollower(
        community_id=community_id,
        user_id=user_id
    )
    db.add(follower)
    db.commit()
    db.refresh(follower)
    return follower


def unfollow_community(db: Session, community_id: int, user_id: int):
    """Unfollow a community"""
    follower = db.query(models.CommunityFollower).filter(
        models.CommunityFollower.community_id == community_id,
        models.CommunityFollower.user_id == user_id
    ).first()
    
    if follower:
        db.delete(follower)
        db.commit()
        return True
    return False


def is_following_community(db: Session, community_id: int, user_id: int):
    """Check if user is following a community"""
    follower = db.query(models.CommunityFollower).filter(
        models.CommunityFollower.community_id == community_id,
        models.CommunityFollower.user_id == user_id
    ).first()
    return follower is not None


def get_community_followers(db: Session, community_id: int):
    """Get all followers of a community"""
    return db.query(models.CommunityFollower).filter(
        models.CommunityFollower.community_id == community_id
    ).all()


# ============= UPDATE EXISTING FUNCTIONS TO TRIGGER NOTIFICATIONS =============

# Update toggle_comment_reaction to create notification
def toggle_comment_reaction(db: Session, comment_id: int, user_id: int, reaction_type: str = "like"):
    """Toggle like/dislike on a comment and create notification"""
    existing = db.query(models.CommentReaction).filter(
        models.CommentReaction.comment_id == comment_id,
        models.CommentReaction.user_id == user_id
    ).first()
    
    # Get the comment to find its author
    comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    
    if existing:
        if existing.reaction_type == reaction_type:
            db.delete(existing)
            db.commit()
            return None
        else:
            existing.reaction_type = reaction_type
            db.commit()
            db.refresh(existing)
            
            # Create notification for comment author (only if not reacting to own comment)
            if comment and comment.user_id != user_id:
                reactor = db.query(models.User).filter(models.User.id == user_id).first()
                create_notification(
                    db=db,
                    user_id=comment.user_id,
                    notification_type='comment_reaction',
                    title='Someone reacted to your comment',
                    message=f'{reactor.username} {reaction_type}d your comment',
                    target_type='comment',
                    target_id=comment_id,
                    actor_id=user_id
                )
            
            return existing
    else:
        reaction = models.CommentReaction(
            comment_id=comment_id,
            user_id=user_id,
            reaction_type=reaction_type
        )
        db.add(reaction)
        db.commit()
        db.refresh(reaction)
        
        # Create notification for comment author (only if not reacting to own comment)
        if comment and comment.user_id != user_id:
            reactor = db.query(models.User).filter(models.User.id == user_id).first()
            create_notification(
                db=db,
                user_id=comment.user_id,
                notification_type='comment_reaction',
                title='Someone reacted to your comment',
                message=f'{reactor.username} {reaction_type}d your comment',
                target_type='comment',
                target_id=comment_id,
                actor_id=user_id
            )
        
        return reaction


# Update create_comment to create notification for replies
def create_comment(db: Session, comment: schemas.CommentCreate, post_id: int, user_id: int):
    db_comment = models.Comment(
        content=comment.content,
        post_id=post_id,
        user_id=user_id
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    
    # Get the post to find its author
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    
    # Create notification for post author (only if not commenting on own post)
    if post and post.user_id != user_id:
        commenter = db.query(models.User).filter(models.User.id == user_id).first()
        create_notification(
            db=db,
            user_id=post.user_id,
            notification_type='comment_reply',
            title='New comment on your post',
            message=f'{commenter.username} commented on your post',
            target_type='post',
            target_id=post_id,
            actor_id=user_id
        )
    
    return db_comment


# Update add_reaction to create notification
def add_reaction(db: Session, post_id: int, user_id: int, reaction_type: str = "like"):
    existing = db.query(models.PostReaction).filter(
        models.PostReaction.post_id == post_id,
        models.PostReaction.user_id == user_id
    ).first()
    
    # Get the post to find its author
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    
    if existing:
        db.delete(existing)
        db.commit()
        return None
    else:
        reaction = models.PostReaction(
            post_id=post_id,
            user_id=user_id,
            reaction_type=reaction_type
        )
        db.add(reaction)
        db.commit()
        db.refresh(reaction)
        
        # Create notification for post author (only if not reacting to own post)
        if post and post.user_id != user_id:
            reactor = db.query(models.User).filter(models.User.id == user_id).first()
            create_notification(
                db=db,
                user_id=post.user_id,
                notification_type='post_reaction',
                title='Someone liked your post',
                message=f'{reactor.username} liked your post: {post.title[:50]}',
                target_type='post',
                target_id=post_id,
                actor_id=user_id
            )
        
        return reaction


# Update create_post to notify community followers
def create_post(db: Session, post: schemas.PostCreate, user_id: int):
    db_post = models.Post(
        title=post.title,
        content=post.content,
        community_id=post.community_id,
        user_id=user_id,
        image_url=post.image_url,
        video_url=post.video_url,
        is_anonymous=post.is_anonymous
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    
    # Notify community followers about new post
    if post.community_id:
        followers = get_community_followers(db, post.community_id)
        author = db.query(models.User).filter(models.User.id == user_id).first()
        community = db.query(models.Community).filter(models.Community.id == post.community_id).first()
        
        for follower in followers:
            # Don't notify the author
            if follower.user_id != user_id:
                create_notification(
                    db=db,
                    user_id=follower.user_id,
                    notification_type='new_post',
                    title=f'New post in {community.name}',
                    message=f'{author.username} posted: {post.title[:50]}',
                    target_type='post',
                    target_id=db_post.id,
                    actor_id=user_id
                )
    
    return db_post

# Community Member Functions
def join_community(db: Session, community_id: int, user_id: int):
    existing = db.query(models.CommunityMember).filter(
        models.CommunityMember.community_id == community_id,
        models.CommunityMember.user_id == user_id
    ).first()
    
    if existing:
        return existing
    
    member = models.CommunityMember(community_id=community_id, user_id=user_id)
    db.add(member)
    db.commit()
    db.refresh(member)
    return member

def leave_community(db: Session, community_id: int, user_id: int):
    member = db.query(models.CommunityMember).filter(
        models.CommunityMember.community_id == community_id,
        models.CommunityMember.user_id == user_id
    ).first()
    
    if member:
        db.delete(member)
        db.commit()
        return True
    return False

def is_community_member(db: Session, community_id: int, user_id: int):
    return db.query(models.CommunityMember).filter(
        models.CommunityMember.community_id == community_id,
        models.CommunityMember.user_id == user_id
    ).first() is not None

def get_community_members_count(db: Session, community_id: int):
    return db.query(models.CommunityMember).filter(
        models.CommunityMember.community_id == community_id
    ).count()