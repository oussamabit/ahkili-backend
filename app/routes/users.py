from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    db_user = crud.get_user_by_firebase_uid(db, firebase_uid=user.firebase_uid)
    if db_user:
        return db_user
    
    # Check if username is taken
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    return crud.create_user(db=db, user=user)

@router.get("/{user_id}", response_model=schemas.UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.get("/firebase/{firebase_uid}", response_model=schemas.UserResponse)
def get_user_by_firebase(firebase_uid: str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_firebase_uid(db, firebase_uid=firebase_uid)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/{user_id}/profile", response_model=schemas.UserProfileResponse)
def update_user_profile(
    user_id: int,
    updates: schemas.UserUpdate,
    db: Session = Depends(get_db)
):
    """Update user profile"""
    # Convert to dict and remove None values
    update_data = {k: v for k, v in updates.dict().items() if v is not None}
    
    # Check if username is being changed and if it's available
    if 'username' in update_data:
        existing_user = crud.get_user_by_username(db, username=update_data['username'])
        if existing_user and existing_user.id != user_id:
            raise HTTPException(status_code=400, detail="Username already taken")
    
    user = crud.update_user_profile(db, user_id=user_id, updates=update_data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get stats
    stats = crud.get_user_profile_stats(db, user_id)
    
    # Convert to response
    response = schemas.UserProfileResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        verified=user.verified,
        bio=user.bio,
        location=user.location,
        profile_picture_url=user.profile_picture_url,
        created_at=user.created_at,
        posts_count=stats['posts_count'],
        communities_count=stats['communities_count']
    )
    
    return response

@router.get("/{user_id}/profile", response_model=schemas.UserProfileResponse)
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    """Get user profile with stats"""
    user = crud.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get stats
    stats = crud.get_user_profile_stats(db, user_id)
    
    response = schemas.UserProfileResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        verified=user.verified,
        bio=user.bio,
        location=user.location,
        profile_picture_url=user.profile_picture_url,
        created_at=user.created_at,
        posts_count=stats['posts_count'],
        communities_count=stats['communities_count']
    )
    
    return response