import cloudinary
import cloudinary.uploader
import os
from fastapi import UploadFile, HTTPException

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

async def upload_image(file: UploadFile) -> str:
    """Upload image to Cloudinary and return URL"""
    try:
        # Check file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Check file size (max 5MB)
        contents = await file.read()
        if len(contents) > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large (max 5MB)")
        
        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            contents,
            folder="ahkili/posts",
            resource_type="image"
        )
        
        return result['secure_url']
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")