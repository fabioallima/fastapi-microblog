from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session, select
from sqlalchemy import Select

from microblog.auth import AuthenticatedUser, get_current_user
from microblog.db import ActiveSession
from microblog.models.post import (
    Post,
    PostRequest,
    PostResponse,
    PostResponseWithReplies,
)
from microblog.models.user import User
from microblog.models.like import Like

router = APIRouter()


@router.get("/", response_model=List[PostResponse])
async def list_posts(*, session: Session = ActiveSession):
    """List all posts without replies"""
    query: Select[Post] = select(Post).where(Post.parent == None)
    posts = session.exec(query).all()
    return posts


@router.get("/{post_id}/", response_model=PostResponseWithReplies)
async def get_post_by_post_id(
    *,
    session: Session = ActiveSession,
    post_id: int,
):
    """Get post by post_id"""
    query: Select[Post] = select(Post).where(Post.id == post_id)
    post = session.exec(query).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.get("/user/{username}/", response_model=List[PostResponse])
async def get_posts_by_username(
    *,
    session: Session = ActiveSession,
    username: str,
    include_replies: bool = False,
):
    """Get posts by username"""
    filters = [User.username == username]
    if not include_replies:
        filters.append(Post.parent == None)
    query: Select[Post] = select(Post).join(User).where(*filters)
    posts = session.exec(query).all()
    return posts


@router.post("/", response_model=PostResponse, status_code=201)
async def create_post(
    *,
    session: Session = ActiveSession,
    user: User = AuthenticatedUser,
    post: PostRequest,
):
    """Creates new post"""
    db_post = Post.model_validate({
        "text": post.text,
        "user_id": user.id,
        "parent_id": post.parent_id
    })
    
    session.add(db_post)
    session.commit()
    session.refresh(db_post)
    return db_post


@router.post("/{post_id}/like/", status_code=status.HTTP_201_CREATED)
def like_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = ActiveSession
):
    """Like a post"""
    # Verifica se o post existe
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # Verifica se o usuário já curtiu o post
    existing_like = session.exec(
        select(Like).where(
            Like.user_id == current_user.id,
            Like.post_id == post_id
        )
    ).first()
    
    if existing_like:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already liked this post"
        )
    
    # Cria o like
    like = Like(user_id=current_user.id, post_id=post_id)
    session.add(like)
    session.commit()
    session.refresh(like)
    
    return {"message": "Post liked successfully"}


@router.get("/likes/{username}/", response_model=List[Post])
def get_user_liked_posts(
    username: str,
    current_user: User = Depends(get_current_user),
    session: Session = ActiveSession
):
    """Get all posts liked by a user"""
    # Busca o usuário
    user = session.exec(
        select(User).where(User.username == username)
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Busca todos os posts curtidos pelo usuário
    liked_posts = session.exec(
        select(Post)
        .join(Like)
        .where(Like.user_id == user.id)
        .order_by(Post.date.desc())
    ).all()
    
    return liked_posts