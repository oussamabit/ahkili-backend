from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db, engine, Base
from app import models

router = APIRouter(prefix="/admin", tags=["admin"])

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