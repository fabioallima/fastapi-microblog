from typing import Optional, TYPE_CHECKING
from datetime import datetime, timezone
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, Integer, DateTime, ForeignKey

if TYPE_CHECKING:
    from microblog.models.user import User

class Social(SQLModel, table=True):
    """Modelo que representa o relacionamento de seguir entre usuários"""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    from_user_id: int = Field(
        sa_column=Column(Integer, ForeignKey("user.id"), name="from")
    )
    to_user_id: int = Field(
        sa_column=Column(Integer, ForeignKey("user.id"), name="to")
    )
    date: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime, name="date")
    )
    
    from_user: "User" = Relationship(
        back_populates="following",
        sa_relationship_kwargs={
            "foreign_keys": "[Social.from_user_id]",
            "primaryjoin": "User.id == Social.from_user_id"
        }
    )
    to_user: "User" = Relationship(
        back_populates="followers",
        sa_relationship_kwargs={
            "foreign_keys": "[Social.to_user_id]",
            "primaryjoin": "User.id == Social.to_user_id"
        }
    ) 