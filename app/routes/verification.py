from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/verification", tags=["verification"])

@router.post("/doctor", response_model=schemas.DoctorVerificationResponse)
def submit_verification(
    verification: schemas.DoctorVerificationCreate,
    user_id: int,
    db: Session = Depends(get_db)
):
    # Check if user already submitted
    existing = crud.get_user_verification(db, user_id=user_id)
    if existing:
        raise HTTPException(status_code=400, detail="Verification already submitted")
    
    return crud.submit_doctor_verification(
        db,
        user_id=user_id,
        full_name=verification.full_name,
        specialization=verification.specialization,
        license_number=verification.license_number,
        license_document_url=verification.license_document_url,
        clinic_address=verification.clinic_address,
        phone_number=verification.phone_number,
        bio=verification.bio
    )

@router.get("/doctor/status")
def get_verification_status(
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    verification = crud.get_user_verification(db, user_id=user_id)
    if not verification:
        return {"status": "not_submitted"}
    
    return {
        "status": verification.status,
        "submitted_at": verification.submitted_at,
        "reviewed_at": verification.reviewed_at,
        "rejection_reason": verification.rejection_reason
    }