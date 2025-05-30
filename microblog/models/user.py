from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, Integer, DateTime, ForeignKey

from microblog.security import HashedPassword
from pydantic import BaseModel

if TYPE_CHECKING:
    from microblog.models.post import Post
    from microblog.models.social import Social
    from microblog.models.like import Like

class User(SQLModel, table=True):
    """Represents the User Model"""
    
    model_config = {"arbitrary_types_allowed": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, nullable=False)
    username: str = Field(unique=True, nullable=False)
    avatar: Optional[str] = Field(default=None)
    bio: Optional[str] = Field(default=None)
    password: HashedPassword

    posts: List["Post"] = Relationship(back_populates="user")
    
    # Relacionamentos para seguir usuários
    following: List["Social"] = Relationship(
        back_populates="from_user",
        sa_relationship_kwargs={
            "foreign_keys": "[Social.from_user_id]",
            "primaryjoin": "User.id == Social.from_user_id"
        }
    )
    followers: List["Social"] = Relationship(
        back_populates="to_user",
        sa_relationship_kwargs={
            "foreign_keys": "[Social.to_user_id]",
            "primaryjoin": "User.id == Social.to_user_id"
        }
    )

    likes: List["Like"] = Relationship(back_populates="user")


class UserResponse(BaseModel):
    """Serializer for User Response"""
    id: int
    username: str
    email: str
    avatar: Optional[str] = None
    bio: Optional[str] = None

    model_config = {
        "from_attributes": True
    }


class UserRequest(BaseModel):
    """Serializer for User Request payload"""
    email: str
    username: str
    password: str
    avatar: Optional[str] = None
    bio: Optional[str] = None