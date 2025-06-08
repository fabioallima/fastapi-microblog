from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from beanie import Document, Link

from microblog.models.user import User

class Post(Document):
    """Post model"""
    content: str
    user: Link[User]
    parent: Optional[Link["Post"]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "posts"
        use_state_management = True


class PostResponse(BaseModel):
    id: str
    content: str
    user_id: str
    parent_id: Optional[str]
    created_at: datetime
    updated_at: datetime


class PostResponseWithReplies(PostResponse):
    """Post response that includes replies"""
    replies: List[PostResponse] = []

    async def get_replies(self):
        """Get all replies for this post"""
        replies = await Post.find(Post.parent.id == self.id).to_list()
        self.replies = [PostResponse.model_validate(reply) for reply in replies]
        return self


class PostCreate(BaseModel):
    content: str
    parent_id: Optional[str] = None


class PostUpdate(BaseModel):
    content: str


class PostRequest(BaseModel):
    parent_id: Optional[str] = None
    text: str

    model_config = {
        "from_attributes": True,
        "extra": "allow"
    }


class TimelineResponse(BaseModel):
    id: str
    text: str
    date: datetime
    user_id: str
    parent_id: Optional[str]

    model_config = {
        "from_attributes": True
    }
