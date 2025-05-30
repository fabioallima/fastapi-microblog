import pytest
from fastapi.testclient import TestClient

def test_create_post(api_client_user1: TestClient):
    """Test creating a new post"""
    response = api_client_user1.post(
        "/post/",
        json={
            "text": "Test post content"
        }
    )
    assert response.status_code == 201
    result = response.json()
    assert result["text"] == "Test post content"
    assert result["parent_id"] is None
    assert "user_id" in result
    assert "date" in result

def test_create_reply(api_client_user1: TestClient, api_client_user2: TestClient):
    """Test creating a reply to a post"""
    # Create original post
    post_response = api_client_user1.post(
        "/post/",
        json={
            "text": "Original post"
        }
    )
    original_post = post_response.json()
    
    # Create reply
    response = api_client_user2.post(
        "/post/",
        json={
            "text": "This is a reply",
            "parent_id": original_post["id"]
        }
    )
    assert response.status_code == 201
    result = response.json()
    assert result["text"] == "This is a reply"
    assert result["parent_id"] == original_post["id"]

def test_list_posts(api_client_user1: TestClient):
    """Test listing all posts without replies"""
    # Create some posts first
    for i in range(3):
        api_client_user1.post(
            "/post/",
            json={
                "text": f"Test post {i+1}"
            }
        )
    
    response = api_client_user1.get("/post/")
    assert response.status_code == 200
    results = response.json()
    for result in results:
        assert result["parent_id"] is None
        assert "text" in result
        assert "user_id" in result
        assert "date" in result

def test_get_post_detail(api_client_user1: TestClient):
    """Test getting post details with replies"""
    # Create post with replies first
    post_response = api_client_user1.post(
        "/post/",
        json={
            "text": "Post with replies"
        }
    )
    post = post_response.json()
    
    # Add some replies
    for i in range(2):
        api_client_user1.post(
            "/post/",
            json={
                "text": f"Reply {i+1}",
                "parent_id": post["id"]
            }
        )
    
    # Get post details
    response = api_client_user1.get(f"/post/{post['id']}/")
    assert response.status_code == 200
    result = response.json()
    assert result["id"] == post["id"]
    assert result["text"] == "Post with replies"
    assert len(result["replies"]) == 2
    for reply in result["replies"]:
        assert reply["parent_id"] == post["id"]
        assert "Reply" in reply["text"]

def test_get_user_posts(api_client_user1: TestClient):
    """Test getting posts from a specific user"""
    # Create some posts
    for i in range(3):
        api_client_user1.post(
            "/post/",
            json={
                "text": f"Post {i+1} from user"
            }
        )
    
    # Get user posts
    response = api_client_user1.get("/post/user/user1/")
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 3
    for result in results:
        assert "Post" in result["text"]

def test_get_user_posts_with_replies(api_client_user1: TestClient):
    """Test getting user posts including replies"""
    # Create post
    post_response = api_client_user1.post(
        "/post/",
        json={
            "text": "Original post"
        }
    )
    post = post_response.json()
    
    # Add replies
    for i in range(2):
        api_client_user1.post(
            "/post/",
            json={
                "text": f"Reply {i+1}",
                "parent_id": post["id"]
            }
        )
    
    # Get user posts with replies
    response = api_client_user1.get(
        "/post/user/user1/",
        params={"include_replies": True}
    )
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 3  # Original post + 2 replies 