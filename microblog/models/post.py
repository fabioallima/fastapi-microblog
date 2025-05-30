from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from pydantic import BaseModel
from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import Column

if TYPE_CHECKING:
    from microblog.models.user import User
    from microblog.models.like import Like


class Post(SQLModel, table=True):
    """Represents the Post Model"""

    id: Optional[int] = Field(default=None, primary_key=True)
    text: str
    date: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    user_id: Optional[int] = Field(foreign_key="user.id")
    parent_id: Optional[int] = Field(foreign_key="post.id")

    # It populates a `.posts` attribute to the `User` model.
    user: Optional["User"] = Relationship(back_populates="posts")

    # It populates `.replies` on this model
    parent: Optional["Post"] = Relationship(
        back_populates="replies",
        sa_relationship_kwargs=dict(remote_side="Post.id"),
    )
    # This lists all children to this post
    replies: list["Post"] = Relationship(back_populates="parent")

    likes: list["Like"] = Relationship(back_populates="post")

    def __lt__(self, other):
        """This enables post.replies.sort() to sort by date"""
        return self.date < other.date


class PostResponse(BaseModel):
    """Serializer for Post Response"""

    id: int
    text: str
    date: datetime
    user_id: int
    parent_id: Optional[int]

    model_config = {
        "from_attributes": True
    }


class PostResponseWithReplies(PostResponse):
    replies: Optional[list["PostResponse"]] = None

    model_config = {
        "from_attributes": True
    }


class PostRequest(BaseModel):
    """Serializer for Post request payload"""

    parent_id: Optional[int] = None
    text: str

    model_config = {
        "from_attributes": True,
        "extra": "allow"
    }


class TimelineResponse(BaseModel):
    """Serializer for Timeline Response"""
    
    id: int
    text: str
    date: datetime
    user_id: int
    parent_id: Optional[int]

    model_config = {
        "from_attributes": True
    }