from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from beanie import PydanticObjectId

from microblog.models.post import (
    Post,
    PostCreate,
    PostUpdate,
    PostResponse,
    PostResponseWithReplies
)
from microblog.models.user import User
from microblog.models.like import Like
from microblog.auth import get_current_user, AuthenticatedUser

router = APIRouter()


@router.get("/", response_model=List[PostResponse])
async def list_posts():
    return await Post.find(Post.parent == None).to_list()


@router.get("/{post_id}/", response_model=PostResponseWithReplies)
async def get_post_by_post_id(post_id: str):
    post = await Post.get(PydanticObjectId(post_id))
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    response = PostResponseWithReplies.model_validate(post)
    return await response.get_replies()


@router.get("/user/{username}/", response_model=List[PostResponse])
async def get_posts_by_username(username: str, include_replies: bool = False):
    user = await User.find_one(User.username == username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if include_replies:
        posts = await Post.find(Post.user.id == user.id).to_list()
    else:
        posts = await Post.find(
            (Post.user.id == user.id) & (Post.parent == None)
        ).to_list()

    return posts


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post: PostCreate,
    current_user: User = AuthenticatedUser,
):
    """Create a new post"""
    if post.parent_id:
        parent = await Post.get(PydanticObjectId(post.parent_id))
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent post not found",
            )

    db_post = Post(
        content=post.content,
        user=current_user,
        parent=parent if post.parent_id else None,
    )
    await db_post.insert()
    
    # Convert to dict and ensure user_id is present
    post_dict = db_post.model_dump()
    if "user_id" not in post_dict and hasattr(current_user, "id"):
        post_dict["user_id"] = str(current_user.id)
    
    return PostResponse.model_validate(post_dict)


@router.post("/{post_id}/like/", status_code=status.HTTP_201_CREATED)
async def like_post(post_id: str, current_user: User = Depends(get_current_user)):
    post = await Post.get(PydanticObjectId(post_id))
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    existing_like = await Like.find_one(
        Like.user_id == current_user.id, Like.post_id == post.id
    )
    if existing_like:
        raise HTTPException(status_code=400, detail="You already liked this post")

    like = Like(user_id=current_user.id, post_id=post.id)
    await like.insert()
    return {"message": "Post liked successfully"}


@router.get("/likes/{username}/", response_model=List[PostResponse])
async def get_user_liked_posts(username: str):
    user = await User.find_one(User.username == username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    likes = await Like.find(Like.user_id == user.id).to_list()
    post_ids = [like.post_id for like in likes]
    posts = await Post.find(Post.id.in_(post_ids)).sort("-date").to_list()
    return posts
