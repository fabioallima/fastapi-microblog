from datetime import datetime
from pydantic import BaseModel, Field
from beanie import Document, Link

from microblog.models.user import User

class Social(Document):
    """Follow relationship"""
    follower: Link[User]
    following: Link[User]
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "social"
        use_state_management = True
        indexes = [
            [("follower", 1), ("following", 1)]
        ]


class SocialResponse(BaseModel):
    id: str
    follower_id: str
    following_id: str
    created_at: datetime


class SocialCreate(BaseModel):
    following_id: str
