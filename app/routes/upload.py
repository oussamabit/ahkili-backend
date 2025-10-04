from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.upload import upload_image

router = APIRouter(prefix="/upload", tags=["upload"])

@router.post("/image")
async def upload_image_endpoint(file: UploadFile = File(...)):
    """Upload an image and return the URL"""
    try:
        url = await upload_image(file)
        return {
            "success": True,
            "url": url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))