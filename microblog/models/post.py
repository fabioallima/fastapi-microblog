from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from beanie import Document, Link
from bson import ObjectId
import logging

from microblog.models.user import User

logger = logging.getLogger(__name__)

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

    def model_dump(self, **kwargs):
        data = super().model_dump(**kwargs)
        logger.debug(f"Original model_dump data: {data}")
        
        # Convert _id to id
        if "_id" in data:
            data["id"] = str(data.pop("_id"))
        
        # Handle user field
        if "user" in data:
            if isinstance(data["user"], dict):
                data["user_id"] = str(data["user"].get("id", data["user"].get("_id")))
            elif isinstance(data["user"], Link):
                data["user_id"] = str(data["user"].ref.id)
            elif hasattr(data["user"], "id"):
                data["user_id"] = str(data["user"].id)
            elif hasattr(data["user"], "_id"):
                data["user_id"] = str(data["user"]._id)
            data.pop("user")
        
        # Handle parent field
        if "parent" in data:
            if data["parent"] is None:
                data["parent_id"] = None
            elif isinstance(data["parent"], dict):
                data["parent_id"] = str(data["parent"].get("id", data["parent"].get("_id")))
            elif isinstance(data["parent"], Link):
                data["parent_id"] = str(data["parent"].ref.id)
            elif hasattr(data["parent"], "id"):
                data["parent_id"] = str(data["parent"].id)
            elif hasattr(data["parent"], "_id"):
                data["parent_id"] = str(data["parent"]._id)
            data.pop("parent")
        
        logger.debug(f"Processed model_dump data: {data}")
        return data


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
