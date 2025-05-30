from typing import Optional
from datetime import datetime
from pydantic import EmailStr, BaseModel, Field
from beanie import Document

class User(Document):
    """User model"""
    username: str = Field(unique=True)
    email: EmailStr = Field(unique=True)
    password_hash: str
    bio: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"
        use_state_management = True


class UserResponse(BaseModel):
    id: str
    username: str
    email: EmailStr
    bio: Optional[str]
    created_at: datetime
    updated_at: datetime


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    bio: Optional[str] = None


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    bio: Optional[str] = None
    password: Optional[str] = None


class UserRequest(BaseModel):
    email: str
    username: str
    password: str
    avatar: Optional[str] = None
    bio: Optional[str] = None
