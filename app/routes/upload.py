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
    
@router.post("/video")
async def upload_video_endpoint(file: UploadFile = File(...)):
    """Upload a video and return the URL"""
    try:
        from app.services.upload import upload_video
        url = await upload_video(file)
        return {
            "success": True,
            "url": url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))