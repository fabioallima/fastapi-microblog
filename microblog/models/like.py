from datetime import datetime
from pydantic import BaseModel, Field
from beanie import Document, Link

from microblog.models.user import User
from microblog.models.post import Post

class Like(Document):
    """Like model"""
    user: Link[User]
    post: Link[Post]
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "likes"
        use_state_management = True
        indexes = [
            [("user", 1), ("post", 1)]  # Evita likes duplicados
        ]


class LikeResponse(BaseModel):
    id: str
    user_id: str
    post_id: str
    created_at: datetime


class LikeCreate(BaseModel):
    post_id: str
