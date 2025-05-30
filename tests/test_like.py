import pytest
from fastapi.testclient import TestClient

def test_like_post(api_client_user1: TestClient, api_client_user2: TestClient):
    """Test liking a post"""
    # User2 creates a post
    post_response = api_client_user2.post(
        "/post/",
        json={
            "text": "Post to be liked"
        }
    )
    post = post_response.json()
    
    # User1 likes the post
    response = api_client_user1.post(f"/post/{post['id']}/like/")
    assert response.status_code == 201
    assert "Post liked successfully" in response.json()["message"]
    
    # Try to like the same post again
    response = api_client_user1.post(f"/post/{post['id']}/like/")
    assert response.status_code == 400
    assert "already liked" in response.json()["detail"]

def test_like_nonexistent_post(api_client_user1: TestClient):
    """Test liking a post that doesn't exist"""
    response = api_client_user1.post("/post/99999/like/")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_get_user_liked_posts(api_client_user1: TestClient, api_client_user2: TestClient):
    """Test getting posts liked by a user"""
    # User2 creates some posts
    posts = []
    for i in range(3):
        post_response = api_client_user2.post(
            "/post/",
            json={
                "text": f"Post {i+1} from user2"
            }
        )
        posts.append(post_response.json())
    
    # User1 likes two posts
    api_client_user1.post(f"/post/{posts[0]['id']}/like/")
    api_client_user1.post(f"/post/{posts[2]['id']}/like/")
    
    # Get User1's liked posts
    response = api_client_user1.get("/post/likes/user1/")
    assert response.status_code == 200
    liked_posts = response.json()
    assert len(liked_posts) == 2
    
    # Verify the liked posts
    liked_post_ids = {post["id"] for post in liked_posts}
    assert posts[0]["id"] in liked_post_ids
    assert posts[2]["id"] in liked_post_ids
    assert posts[1]["id"] not in liked_post_ids

def test_get_likes_nonexistent_user(api_client_user1: TestClient):
    """Test getting likes from a user that doesn't exist"""
    response = api_client_user1.get("/post/likes/nonexistent/")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_like_post_unauthorized(api_client: TestClient):
    """Test liking a post without authentication"""
    response = api_client.post("/post/1/like/")
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]

def test_get_likes_unauthorized(api_client: TestClient):
    """Test getting likes without authentication"""
    response = api_client.get("/post/likes/user1/")
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"] 