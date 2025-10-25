import cloudinary
import cloudinary.uploader
import os
from fastapi import UploadFile, HTTPException
import re

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
            resource_type="image",
            transformation=[
                {'width': 800, 'height': 800, 'crop': 'limit'},
                {'quality': 'auto'}
            ]
        )
        
        print(f"Upload successful: {result['secure_url']}")
        return result['secure_url']
    except Exception as e:
        print(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

async def upload_video(file: UploadFile) -> str:
    """Upload video to Cloudinary and return URL"""
    try:
        # Check file type
        if not file.content_type.startswith('video/'):
            raise HTTPException(status_code=400, detail="File must be a video")
        
        # Check file size (max 50MB for videos)
        contents = await file.read()
        if len(contents) > 50 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Video too large (max 50MB)")
        
        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            contents,
            resource_type="video",
            transformation=[
                {'width': 1280, 'height': 720, 'crop': 'limit'},
                {'quality': 'auto'}
            ]
        )
        
        print(f"Video upload successful: {result['secure_url']}")
        return result['secure_url']
    except Exception as e:
        print(f"Video upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Video upload failed: {str(e)}")

def delete_image(image_url: str) -> bool:
    """Delete image from Cloudinary using its URL"""
    try:
        # Extract public_id from URL
        # URL format: https://res.cloudinary.com/cloud_name/image/upload/v1234567890/public_id.jpg
        match = re.search(r'/v\d+/(.+)\.\w+$', image_url)
        if not match:
            print(f"Could not extract public_id from URL: {image_url}")
            return False
        
        public_id = match.group(1)
        print(f"Deleting image with public_id: {public_id}")
        
        result = cloudinary.uploader.destroy(public_id)
        print(f"Delete result: {result}")
        return result.get('result') == 'ok'
    except Exception as e:
        print(f"Delete error: {str(e)}")
        return False

def delete_video(video_url: str) -> bool:
    """Delete video from Cloudinary using its URL"""
    try:
        # Extract public_id from URL
        match = re.search(r'/v\d+/(.+)\.\w+$', video_url)
        if not match:
            print(f"Could not extract public_id from URL: {video_url}")
            return False
        
        public_id = match.group(1)
        print(f"Deleting video with public_id: {public_id}")
        
        result = cloudinary.uploader.destroy(public_id, resource_type="video")
        print(f"Delete result: {result}")
        return result.get('result') == 'ok'
    except Exception as e:
        print(f"Delete error: {str(e)}")
        return False