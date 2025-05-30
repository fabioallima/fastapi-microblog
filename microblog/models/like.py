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
    user_id: int = Field(
        sa_column=Column("user", Integer, ForeignKey("user.id"))
    )
    post_id: int = Field(
        sa_column=Column("post", Integer, ForeignKey("post.id"))
    )
    date: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime, name="date")
    )
    
    # Relacionamentos
    user: "User" = Relationship(back_populates="likes")
    post: "Post" = Relationship(back_populates="likes") 