from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from microblog.db import ActiveSession
from microblog.models.user import User, UserRequest, UserResponse
from microblog.models.social import Social
from microblog.models.post import Post
from microblog.security import HashedPassword
from microblog.auth import get_current_user

router = APIRouter()

@router.get("/", response_model=List[UserResponse])
async def list_users(*, session: Session = ActiveSession):
    """List all users"""
    users = session.exec(select(User)).all()
    return users

@router.get("/{username}/", response_model=UserResponse)
async def get_user_by_username(
        *, session: Session = ActiveSession, username: str
):
    """Get user by username"""
    query = select(User).where(User.username == username)
    user = session.exec(query).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        avatar=user.avatar,
        bio=user.bio
    )

@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(*, session: Session = ActiveSession, user: UserRequest):
    """Create new user"""
    # Verifica se o usuário já existe
    existing_user = session.exec(
        select(User).where(
            (User.email == user.email) | (User.username == user.username)
        )
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email or username already registered"
        )
    
    # Cria o usuário com a senha criptografada
    db_user = User.model_validate({
        "email": user.email,
        "username": user.username,
        "password": HashedPassword(user.password),
        "avatar": user.avatar,
        "bio": user.bio
    })
    
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@router.post("/follow/{user_id}", status_code=201)
async def follow_user(
    *,
    session: Session = ActiveSession,
    user_id: int,
    current_user: User = Depends(get_current_user)
):
    """Seguir um usuário"""
    # Verifica se o usuário a ser seguido existe
    user_to_follow = session.get(User, user_id)
    if not user_to_follow:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verifica se não está tentando seguir a si mesmo
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")
    
    # Verifica se já não está seguindo
    existing_follow = session.exec(
        select(Social).where(
            (Social.from_user_id == current_user.id) & 
            (Social.to_user_id == user_id)
        )
    ).first()
    
    if existing_follow:
        raise HTTPException(status_code=400, detail="Already following this user")
    
    # Cria o relacionamento de seguir
    follow = Social(from_user_id=current_user.id, to_user_id=user_id)
    session.add(follow)
    session.commit()
    
    return {"message": f"Now following user {user_to_follow.username}"}

@router.get("/timeline", response_model=List[Post])
async def get_timeline(
    *,
    session: Session = ActiveSession,
    current_user: User = Depends(get_current_user)
):
    """Lista todos os posts dos usuários que o usuário atual segue"""
    # Busca os IDs dos usuários que o usuário atual segue
    following_ids = session.exec(
        select(Social.to_user_id)
        .where(Social.from_user_id == current_user.id)
    ).all()
    
    # Busca os posts desses usuários
    posts = session.exec(
        select(Post)
        .where(Post.user_id.in_(following_ids))
        .order_by(Post.created_at.desc())
    ).all()
    
    return posts
