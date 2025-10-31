# app/routers/communities.py (Updated)
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import crud, schemas, models
from app.database import get_db

router = APIRouter(prefix="/communities", tags=["communities"])

@router.get("/", response_model=List[schemas.CommunityResponse])
def get_communities(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_communities(db, skip=skip, limit=limit)

@router.get("/{community_id}", response_model=schemas.CommunityResponse)
def get_community(community_id: int, db: Session = Depends(get_db)):
    db_community = crud.get_community(db, community_id=community_id)
    if db_community is None:
        raise HTTPException(status_code=404, detail="Community not found")
    return db_community

@router.post("/", response_model=schemas.CommunityResponse)
def create_community(
    name: str,
    description: str,
    created_by: int,
    db: Session = Depends(get_db)
):
    # Check if user is verified doctor or admin
    user = crud.get_user(db, user_id=created_by)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.role not in ['doctor', 'admin']:
        raise HTTPException(
            status_code=403, 
            detail="Only verified professionals can create communities"
        )
    
    # Check if community name already exists
    existing = db.query(models.Community).filter(
        models.Community.name == name
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400, 
            detail="A community with this name already exists"
        )
    
    # Create the community
    community = crud.create_community(
        db=db, 
        name=name, 
        description=description, 
        created_by=created_by
    )
    
    # Automatically assign creator as community moderator
    crud.assign_community_moderator(
        db=db,
        community_id=community.id,
        user_id=created_by,
        assigned_by=created_by
    )
    
    # Auto-join creator to the community
    crud.join_community(db, community.id, created_by)
    
    return community

@router.get("/search", response_model=List[schemas.CommunityResponse])
def search_communities(q: str, db: Session = Depends(get_db)):
    from app import crud as crud_ops
    return crud_ops.search_communities(db, query=q)

@router.post("/{community_id}/join")
def join_community(community_id: int, user_id: int, db: Session = Depends(get_db)):
    # Check if community exists
    community = crud.get_community(db, community_id)
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")
    
    member = crud.join_community(db, community_id, user_id)
    return {"message": "Joined successfully", "member_id": member.id}

@router.delete("/{community_id}/leave")
def leave_community(community_id: int, user_id: int, db: Session = Depends(get_db)):
    success = crud.leave_community(db, community_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Not a member")
    return {"message": "Left successfully"}

@router.get("/{community_id}/check-membership")
def check_membership(community_id: int, user_id: int, db: Session = Depends(get_db)):
    is_member = crud.is_community_member(db, community_id, user_id)
    return {"is_member": is_member}

@router.get("/{community_id}/stats")
def get_community_stats(community_id: int, db: Session = Depends(get_db)):
    """Get community statistics"""
    community = crud.get_community(db, community_id)
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")
    
    posts_count = db.query(models.Post).filter(
        models.Post.community_id == community_id
    ).count()
    
    members_count = crud.get_community_members_count(db, community_id)
    
    return {
        "id": community_id,
        "posts_count": posts_count,
        "members_count": members_count
    }

# Moderator Management Endpoints
@router.post("/{community_id}/moderators")
def add_community_moderator(
    community_id: int,
    user_id: int,
    assigned_by: int,
    db: Session = Depends(get_db)
):
    """Add a moderator to a community (creator or admin only)"""
    # Check if community exists
    community = crud.get_community(db, community_id)
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")
    
    # Check if assigner has permission
    assigner = crud.get_user(db, assigned_by)
    if not assigner:
        raise HTTPException(status_code=404, detail="Assigner not found")
    
    # Only community creator or admin can assign moderators
    if community.created_by != assigned_by and assigner.role != 'admin':
        raise HTTPException(
            status_code=403, 
            detail="Only community creator or admins can assign moderators"
        )
    
    # Check if user to be assigned exists
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if already a moderator
    if crud.is_community_moderator(db, community_id, user_id):
        raise HTTPException(
            status_code=400, 
            detail="User is already a moderator"
        )
    
    moderator = crud.assign_community_moderator(
        db=db,
        community_id=community_id,
        user_id=user_id,
        assigned_by=assigned_by
    )
    
    return {"message": "Moderator assigned successfully", "moderator_id": moderator.id}

@router.delete("/{community_id}/moderators/{user_id}")
def remove_community_moderator(
    community_id: int,
    user_id: int,
    removed_by: int,
    db: Session = Depends(get_db)
):
    """Remove a moderator from a community"""
    community = crud.get_community(db, community_id)
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")
    
    # Check permissions
    remover = crud.get_user(db, removed_by)
    if not remover:
        raise HTTPException(status_code=404, detail="User not found")
    
    if community.created_by != removed_by and remover.role != 'admin':
        raise HTTPException(
            status_code=403, 
            detail="Only community creator or admins can remove moderators"
        )
    
    # Can't remove community creator as moderator
    if community.created_by == user_id:
        raise HTTPException(
            status_code=400, 
            detail="Cannot remove community creator as moderator"
        )
    
    success = crud.remove_community_moderator(db, community_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Moderator not found")
    
    return {"message": "Moderator removed successfully"}

@router.get("/{community_id}/moderators")
def get_community_moderators(community_id: int, db: Session = Depends(get_db)):
    """Get all moderators of a community"""
    community = crud.get_community(db, community_id)
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")
    
    moderators = crud.get_community_moderators(db, community_id)
    
    # Get user details for each moderator
    moderator_details = []
    for mod in moderators:
        user = crud.get_user(db, mod.user_id)
        if user:
            moderator_details.append({
                "id": mod.id,
                "user_id": user.id,
                "username": user.username,
                "assigned_at": mod.assigned_at,
                "is_creator": user.id == community.created_by
            })
    
    return moderator_details