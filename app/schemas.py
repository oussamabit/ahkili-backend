from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# User schemas
class UserCreate(BaseModel):
    firebase_uid: str
    username: str
    email: EmailStr

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Post schemas
class PostCreate(BaseModel):
    title: str
    content: str
    community_id: Optional[int] = None
    image_url: Optional[str] = None

class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    user_id: int
    community_id: Optional[int]
    image_url: Optional[str] = None  
    created_at: datetime
    
    class Config:
        from_attributes = True

# Comment schemas
class CommentCreate(BaseModel):
    content: str

class CommentResponse(BaseModel):
    id: int
    content: str
    user_id: int
    post_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Community schemas
class CommunityResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Reaction schemas
class ReactionCreate(BaseModel):
    reaction_type: str = "like"

class ReactionResponse(BaseModel):
    id: int
    post_id: int
    user_id: int
    reaction_type: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Update PostResponse to include reactions count
class PostResponseWithReactions(PostResponse):
    reactions_count: int = 0
    user_has_reacted: bool = False

# Report schemas
class ReportCreate(BaseModel):
    target_type: str
    target_id: int
    reason: str

class ReportResponse(BaseModel):
    id: int
    reported_by: Optional[int]
    target_type: str
    target_id: int
    reason: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# User with role
class UserWithRole(BaseModel):
    id: int
    username: str
    email: str
    role: str
    verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True