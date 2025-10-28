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
    video_url: Optional[str] = None
    is_anonymous: bool = False

class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    user_id: int
    community_id: Optional[int]
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    is_anonymous: bool = False
    created_at: datetime
    reactions_count: int = 0
    comments_count: int = 0
    
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
    parent_id: Optional[int] = None
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

# Doctor Verification schemas
class DoctorVerificationCreate(BaseModel):
    full_name: str
    specialization: str
    license_number: str
    license_document_url: str
    clinic_address: str
    phone_number: str
    bio: str

class DoctorVerificationResponse(BaseModel):
    id: int
    user_id: int
    full_name: str
    specialization: str
    license_number: str
    license_document_url: str
    clinic_address: str
    phone_number: str
    bio: str
    status: str
    submitted_at: datetime
    reviewed_at: Optional[datetime]
    rejection_reason: Optional[str]
    
    class Config:
        from_attributes = True

# Community Moderator schemas
class CommunityModeratorCreate(BaseModel):
    community_id: int
    user_id: int

class CommunityModeratorResponse(BaseModel):
    id: int
    community_id: int
    user_id: int
    assigned_at: datetime
    
    class Config:
        from_attributes = True

# Notification Preference schemas
class NotificationPreferenceCreate(BaseModel):
    email_notifications: bool = True
    push_notifications: bool = False
    comment_reactions: bool = True
    comment_replies: bool = True
    post_reactions: bool = True
    new_posts: bool = False

class NotificationPreferenceResponse(BaseModel):
    id: int
    user_id: int
    email_notifications: bool
    push_notifications: bool
    comment_reactions: bool
    comment_replies: bool
    post_reactions: bool
    new_posts: bool
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Notification schemas
class NotificationResponse(BaseModel):
    id: int
    user_id: int
    type: str
    title: str
    message: str
    target_type: Optional[str]
    target_id: Optional[int]
    actor_id: Optional[int]
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Community Follower schemas
class CommunityFollowerCreate(BaseModel):
    community_id: int

class CommunityFollowerResponse(BaseModel):
    id: int
    community_id: int
    user_id: int
    followed_at: datetime
    
    class Config:
        from_attributes = True