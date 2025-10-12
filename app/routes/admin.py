from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db, engine, Base
from app import models, crud, schemas
from typing import List

router = APIRouter(prefix="/admin", tags=["admin"])

def verify_admin(user_id: int, db: Session = Depends(get_db)):
    """Verify user is admin or moderator"""
    user = crud.get_user(db, user_id)
    if not user or user.role not in ['admin', 'moderator']:
        raise HTTPException(status_code=403, detail="Not authorized")
    return user

@router.post("/init-db")
def initialize_database():
    """Initialize database tables - run this once after deployment"""
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        return {
            "success": True,
            "message": "Database tables created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/seed-communities")
def seed_communities(db: Session = Depends(get_db)):
    """Seed initial communities"""
    communities_data = [
        {
            "name": "Anxiety Support",
            "description": "A safe space for people dealing with anxiety. Share experiences, coping strategies, and support each other."
        },
        {
            "name": "Depression Support",
            "description": "Connect with others who understand depression. You are not alone in this journey."
        },
        {
            "name": "Mindfulness & Meditation",
            "description": "Practice mindfulness together. Share meditation techniques and peaceful living tips."
        },
        {
            "name": "PTSD Recovery",
            "description": "Support group for PTSD survivors. A judgment-free zone for healing and recovery."
        },
        {
            "name": "Self-Care & Wellness",
            "description": "Focus on self-care routines, healthy habits, and overall mental wellness."
        },
        {
            "name": "Stress Management",
            "description": "Learn and share stress management techniques. Build resilience together."
        },
    ]
    
    created = []
    for comm_data in communities_data:
        # Check if exists
        existing = db.query(models.Community).filter(
            models.Community.name == comm_data["name"]
        ).first()
        
        if not existing:
            # Get first user or create a system user
            user = db.query(models.User).first()
            if not user:
                # Create system user
                user = models.User(
                    firebase_uid="system",
                    username="system",
                    email="system@ahkili.app"
                )
                db.add(user)
                db.commit()
                db.refresh(user)
            
            community = models.Community(
                name=comm_data["name"],
                description=comm_data["description"],
                created_by=user.id
            )
            db.add(community)
            created.append(comm_data["name"])
    
    db.commit()
    
    return {
        "success": True,
        "created": created,
        "message": f"Created {len(created)} communities"
    }

# ============= USER MANAGEMENT =============
@router.get("/users", response_model=List[schemas.UserWithRole])
def get_all_users(
    admin_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    verify_admin(admin_id, db)
    return crud.get_all_users(db, skip=skip, limit=limit)

@router.post("/promote-user")
def promote_user(
    admin_id: int,
    user_id: int,
    role: str,
    db: Session = Depends(get_db)
):
    admin = verify_admin(admin_id, db)
    if admin.role != 'admin':
        raise HTTPException(status_code=403, detail="Only admins can promote users")
    
    if role not in ['user', 'moderator', 'admin', 'doctor']:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    user = crud.promote_user(db, user_id=user_id, role=role)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"success": True, "user": user}

@router.post("/ban-user")
def ban_user(
    admin_id: int,
    user_id: int,
    reason: str,
    db: Session = Depends(get_db)
):
    verify_admin(admin_id, db)
    
    success = crud.ban_user(db, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Log the action
    crud.create_moderation_log(
        db,
        moderator_id=admin_id,
        action='ban_user',
        target_type='user',
        target_id=user_id,
        reason=reason
    )
    
    return {"success": True, "message": "User banned"}

# ============= REPORTS =============
@router.post("/reports", response_model=schemas.ReportResponse)
def create_report(
    report: schemas.ReportCreate,
    user_id: int,
    db: Session = Depends(get_db)
):
    return crud.create_report(
        db,
        reported_by=user_id,
        target_type=report.target_type,
        target_id=report.target_id,
        reason=report.reason
    )

@router.get("/reports", response_model=List[schemas.ReportResponse])
def get_reports(
    admin_id: int,
    status: str = None,
    db: Session = Depends(get_db)
):
    verify_admin(admin_id, db)
    return crud.get_reports(db, status=status)

@router.post("/reports/{report_id}/resolve")
def resolve_report(
    report_id: int,
    admin_id: int,
    db: Session = Depends(get_db)
):
    verify_admin(admin_id, db)
    
    success = crud.resolve_report(db, report_id=report_id, resolved_by=admin_id)
    if not success:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return {"success": True, "message": "Report resolved"}

# ============= CONTENT MODERATION =============
@router.delete("/posts/{post_id}/moderate")
def moderate_delete_post(
    post_id: int,
    admin_id: int,
    reason: str,
    db: Session = Depends(get_db)
):
    verify_admin(admin_id, db)
    
    # Delete post
    image_url = crud.delete_post(db, post_id=post_id)
    
    # Delete image if exists
    if image_url:
        from app.services.upload import delete_image
        delete_image(image_url)
    
    # Log the action
    crud.create_moderation_log(
        db,
        moderator_id=admin_id,
        action='delete_post',
        target_type='post',
        target_id=post_id,
        reason=reason
    )
    
    return {"success": True, "message": "Post deleted"}

# ============= DOCTOR VERIFICATION =============
@router.get("/doctor-verifications", response_model=List[schemas.DoctorVerificationResponse])
def get_doctor_verifications(
    admin_id: int,
    status: str = None,
    db: Session = Depends(get_db)
):
    verify_admin(admin_id, db)
    
    if status == 'pending':
        return crud.get_pending_verifications(db)
    else:
        return crud.get_all_verifications(db)

@router.post("/doctor-verifications/{verification_id}/approve")
def approve_verification(
    verification_id: int,
    admin_id: int,
    db: Session = Depends(get_db)
):
    admin = verify_admin(admin_id, db)
    if admin.role != 'admin':
        raise HTTPException(status_code=403, detail="Only admins can approve verifications")
    
    verification = crud.approve_doctor_verification(db, verification_id=verification_id, admin_id=admin_id)
    if not verification:
        raise HTTPException(status_code=404, detail="Verification not found")
    
    # Log the action
    crud.create_moderation_log(
        db,
        moderator_id=admin_id,
        action='approve_doctor',
        target_type='verification',
        target_id=verification_id,
        reason='Doctor verified'
    )
    
    return {"success": True, "message": "Doctor verification approved"}

@router.post("/doctor-verifications/{verification_id}/reject")
def reject_verification(
    verification_id: int,
    admin_id: int,
    reason: str,
    db: Session = Depends(get_db)
):
    admin = verify_admin(admin_id, db)
    if admin.role != 'admin':
        raise HTTPException(status_code=403, detail="Only admins can reject verifications")
    
    verification = crud.reject_doctor_verification(
        db,
        verification_id=verification_id,
        admin_id=admin_id,
        reason=reason
    )
    
    if not verification:
        raise HTTPException(status_code=404, detail="Verification not found")
    
    return {"success": True, "message": "Doctor verification rejected"}

# ============= COMMUNITY MODERATORS =============
@router.post("/communities/{community_id}/moderators")
def assign_community_mod(
    community_id: int,
    user_id: int,
    admin_id: int,
    db: Session = Depends(get_db)
):
    verify_admin(admin_id, db)
    
    # Check if community exists
    community = crud.get_community(db, community_id=community_id)
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")
    
    # Check if user exists
    user = crud.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    moderator = crud.assign_community_moderator(
        db,
        community_id=community_id,
        user_id=user_id,
        assigned_by=admin_id
    )
    
    return {"success": True, "moderator": moderator}

@router.delete("/communities/{community_id}/moderators/{user_id}")
def remove_community_mod(
    community_id: int,
    user_id: int,
    admin_id: int,
    db: Session = Depends(get_db)
):
    verify_admin(admin_id, db)
    
    success = crud.remove_community_moderator(db, community_id=community_id, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Moderator not found")
    
    return {"success": True, "message": "Moderator removed"}

@router.get("/communities/{community_id}/moderators")
def get_community_mods(
    community_id: int,
    db: Session = Depends(get_db)
):
    return crud.get_community_moderators(db, community_id=community_id)