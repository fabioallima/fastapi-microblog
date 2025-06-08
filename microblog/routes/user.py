from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from beanie import PydanticObjectId

from microblog.models.user import User, UserCreate, UserUpdate, UserResponse
from microblog.models.social import Social
from microblog.models.post import TimelineResponse, Post, PostResponse
from microblog.security import get_password_hash
from microblog.auth import get_current_user, AuthenticatedUser

router = APIRouter()


@router.get("/", response_model=List[UserResponse])
async def list_users():
    return await User.find_all().to_list()


@router.get("/{username}/", response_model=UserResponse)
async def get_user_by_username(username: str):
    user = await User.find_one(User.username == username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    """Create a new user"""
    if await User.find_one({"username": user.username}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    if await User.find_one({"email": user.email}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    db_user = User(
        username=user.username,
        email=user.email,
        password_hash=get_password_hash(user.password),
        bio=user.bio,
    )
    await db_user.insert()
    return db_user


@router.post("/follow/{user_id}", status_code=201)
async def follow_user(user_id: str, current_user: User = Depends(get_current_user)):
    if user_id == str(current_user.id):
        raise HTTPException(status_code=400, detail="Cannot follow yourself")

    user_to_follow = await User.get(PydanticObjectId(user_id))
    if not user_to_follow:
        raise HTTPException(status_code=404, detail="User not found")

    existing_follow = await Social.find_one(
        Social.from_user_id == current_user.id,
        Social.to_user_id == PydanticObjectId(user_id)
    )
    if existing_follow:
        raise HTTPException(status_code=400, detail="Already following this user")

    follow = Social(from_user_id=current_user.id, to_user_id=PydanticObjectId(user_id))
    await follow.insert()
    return {"message": f"Now following user {user_to_follow.username}"}


@router.get("/timeline", response_model=List[TimelineResponse])
async def get_timeline(current_user: User = Depends(get_current_user)):
    follows = await Social.find(Social.from_user_id == current_user.id).to_list()
    followed_user_ids = [follow.to_user_id for follow in follows]

    if not followed_user_ids:
        return []

    posts = await Post.find(Post.user.id.in_(followed_user_ids)).sort("-date").to_list()
    return [TimelineResponse.model_validate(post) for post in posts]


@router.get("/{user_id}/posts", response_model=List[PostResponse])
async def read_user_posts(user_id: str):
    """Get all posts from a user"""
    user = await User.get(PydanticObjectId(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    posts = await Post.find({"user.id": user.id}).to_list()
    return posts
