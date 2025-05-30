import pytest
from fastapi.testclient import TestClient

def test_follow_user(api_client_user1: TestClient, api_client_user2: TestClient):
    """Test following a user"""
    # Get user2's ID
    user2_response = api_client_user2.get("/user/user2/")
    user2 = user2_response.json()
    
    # User1 follows User2
    response = api_client_user1.post(f"/user/follow/{user2['id']}")
    assert response.status_code == 201
    assert "Now following user user2" in response.json()["message"]

def test_follow_nonexistent_user(api_client_user1: TestClient):
    """Test following a user that doesn't exist"""
    response = api_client_user1.post("/user/follow/99999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_follow_self(api_client_user1: TestClient):
    """Test trying to follow yourself"""
    # Get user1's ID
    user1_response = api_client_user1.get("/user/user1/")
    user1 = user1_response.json()
    
    response = api_client_user1.post(f"/user/follow/{user1['id']}")
    assert response.status_code == 400
    assert "Cannot follow yourself" in response.json()["detail"]

def test_follow_already_following(api_client_user1: TestClient, api_client_user2: TestClient):
    """Test following a user you already follow"""
    # Get user2's ID
    user2_response = api_client_user2.get("/user/user2/")
    user2 = user2_response.json()
    
    # First follow
    api_client_user1.post(f"/user/follow/{user2['id']}")
    
    # Try to follow again
    response = api_client_user1.post(f"/user/follow/{user2['id']}")
    assert response.status_code == 400
    assert "Already following this user" in response.json()["detail"]

def test_timeline_empty(api_client_user1: TestClient):
    """Test timeline when not following anyone"""
    response = api_client_user1.get("/user/timeline")
    assert response.status_code == 200
    assert response.json() == []

def test_timeline_with_posts(api_client_user1: TestClient, api_client_user2: TestClient):
    """Test timeline with posts from followed users"""
    # Get user2's ID
    user2_response = api_client_user2.get("/user/user2/")
    user2 = user2_response.json()
    
    # User1 follows User2
    api_client_user1.post(f"/user/follow/{user2['id']}")
    
    # User2 creates some posts
    for i in range(3):
        api_client_user2.post(
            "/post/",
            json={
                "text": f"Post {i+1} from user2"
            }
        )
    
    # Check User1's timeline
    response = api_client_user1.get("/user/timeline")
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 3
    for result in results:
        assert result["user_id"] == user2["id"]
        assert "Post" in result["text"]
        assert "date" in result
        assert "parent_id" in result

def test_timeline_with_replies(api_client_user1: TestClient, api_client_user2: TestClient):
    """Test timeline includes both posts and replies"""
    # Get user2's ID
    user2_response = api_client_user2.get("/user/user2/")
    user2 = user2_response.json()
    
    # User1 follows User2
    api_client_user1.post(f"/user/follow/{user2['id']}")
    
    # User2 creates a post
    post_response = api_client_user2.post(
        "/post/",
        json={
            "text": "Original post from user2"
        }
    )
    post = post_response.json()
    
    # User2 adds replies to their own post
    for i in range(2):
        api_client_user2.post(
            "/post/",
            json={
                "text": f"Reply {i+1} from user2",
                "parent_id": post["id"]
            }
        )
    
    # Check User1's timeline
    response = api_client_user1.get("/user/timeline")
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 3  # Original post + 2 replies
    
    # Verify the original post
    original_post = next(post for post in results if post["parent_id"] is None)
    assert original_post["text"] == "Original post from user2"
    assert original_post["user_id"] == user2["id"]
    
    # Verify the replies
    replies = [post for post in results if post["parent_id"] is not None]
    assert len(replies) == 2
    for reply in replies:
        assert reply["parent_id"] == post["id"]
        assert reply["user_id"] == user2["id"]
        assert "Reply" in reply["text"] 