from sqlalchemy.orm import Session
from app import models, schemas
from typing import List, Optional

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
    return query.order_by(models.Post.created_at.desc()).offset(skip).limit(limit).all()

def get_post(db: Session, post_id: int):
    return db.query(models.Post).filter(models.Post.id == post_id).first()

def create_post(db: Session, post: schemas.PostCreate, user_id: int):
    db_post = models.Post(
        title=post.title,
        content=post.content,
        community_id=post.community_id,
        user_id=user_id,
        image_url=post.image_url  
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

def delete_post(db: Session, post_id: int):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post:
        # Store image_url before deleting
        image_url = post.image_url
        
        # Delete post from database
        db.delete(post)
        db.commit()
        
        # Return image_url so we can delete it from Cloudinary
        return image_url
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
    return db.query(models.Post).filter(models.Post.user_id == user_id).order_by(models.Post.created_at.desc()).all()

# ============= SEARCH FUNCTIONS =============
def search_posts(db: Session, query: str, skip: int = 0, limit: int = 50):
    return db.query(models.Post).filter(
        models.Post.title.ilike(f'%{query}%') | models.Post.content.ilike(f'%{query}%')
    ).order_by(models.Post.created_at.desc()).offset(skip).limit(limit).all()

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