from typing import List

from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from sqlmodel import Session, select

from microblog.db import ActiveSession
from microblog.models.user import User, UserRequest, UserResponse
from microblog.security import HashedPassword

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
