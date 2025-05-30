import pytest
from fastapi.testclient import TestClient

def test_create_user(api_client: TestClient):
    """Test creating a new user"""
    response = api_client.post(
        "/user/",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpass123",
            "avatar": "https://example.com/avatar.jpg",
            "bio": "Test bio"
        }
    )
    assert response.status_code == 201
    result = response.json()
    assert result["email"] == "test@example.com"
    assert result["username"] == "testuser"
    assert result["avatar"] == "https://example.com/avatar.jpg"
    assert result["bio"] == "Test bio"
    assert "password" not in result

def test_create_duplicate_user(api_client: TestClient):
    """Test creating a user with existing email/username"""
    # First user
    api_client.post(
        "/user/",
        json={
            "email": "duplicate@example.com",
            "username": "duplicate",
            "password": "testpass123"
        }
    )
    
    # Try to create user with same email
    response = api_client.post(
        "/user/",
        json={
            "email": "duplicate@example.com",
            "username": "different",
            "password": "testpass123"
        }
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]
    
    # Try to create user with same username
    response = api_client.post(
        "/user/",
        json={
            "email": "different@example.com",
            "username": "duplicate",
            "password": "testpass123"
        }
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]

def test_get_user_by_username(api_client: TestClient):
    """Test getting user by username"""
    # Create user first
    api_client.post(
        "/user/",
        json={
            "email": "getuser@example.com",
            "username": "getuser",
            "password": "testpass123"
        }
    )
    
    response = api_client.get("/user/getuser/")
    assert response.status_code == 200
    result = response.json()
    assert result["username"] == "getuser"
    assert result["email"] == "getuser@example.com"
    assert "password" not in result

def test_get_nonexistent_user(api_client: TestClient):
    """Test getting a user that doesn't exist"""
    response = api_client.get("/user/nonexistent/")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_list_users(api_client: TestClient):
    """Test listing all users"""
    # Create some users first
    for i in range(3):
        api_client.post(
            "/user/",
            json={
                "email": f"user{i}@example.com",
                "username": f"user{i}",
                "password": "testpass123"
            }
        )
    
    response = api_client.get("/user/")
    assert response.status_code == 200
    results = response.json()
    assert len(results) >= 3  # At least the users we just created
    for result in results:
        assert "username" in result
        assert "email" in result
        assert "password" not in result 