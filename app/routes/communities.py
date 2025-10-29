from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import crud, schemas
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
    return crud.create_community(db=db, name=name, description=description, created_by=created_by)

@router.get("/search", response_model=List[schemas.CommunityResponse])
def search_communities(q: str, db: Session = Depends(get_db)):
    from app import crud as crud_ops
    return crud_ops.search_communities(db, query=q)

@router.post("/{community_id}/join")
def join_community(community_id: int, user_id: int, db: Session = Depends(get_db)):
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