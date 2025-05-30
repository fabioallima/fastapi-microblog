from typing import Optional, TYPE_CHECKING
from datetime import datetime, timezone
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, Integer, DateTime, ForeignKey

if TYPE_CHECKING:
    from microblog.models.user import User
    from microblog.models.post import Post

class Like(SQLModel, table=True):
    """Modelo que representa o like de um usuário em um post"""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user: int = Field(foreign_key="user.id")
    post: int = Field(foreign_key="post.id")
    date: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime, name="date")
    )
    
    # Relacionamentos
    user_rel: "User" = Relationship(back_populates="likes")
    post_rel: "Post" = Relationship(back_populates="likes") 