import pytest
from fastapi import status

def test_register_user(client):
    """Test user registration."""
    user_data = {
        "email": "newuser@example.com",
        "password": "SecurePass123!",
        "full_name": "New User"
    }
    
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == status.HTTP_201_CREATED
    
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]
    assert "id" in data
    assert "hashed_password" not in data

def test_register_user_duplicate_email(client, test_user):
    """Test registration with duplicate email."""
    user_data = {
        "email": test_user.email,
        "password": "SecurePass123!",
        "full_name": "Another User"
    }
    
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Email already registered" in response.json()["detail"]

def test_login_user(client, test_user):
    """Test user login."""
    login_data = {
        "username": test_user.email,
        "password": "password123"
    }
    
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    login_data = {
        "username": "nonexistent@example.com",
        "password": "wrongpassword"
    }
    
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_current_user(client, test_user):
    """Test getting current user with valid token."""
    # First login to get token
    login_data = {
        "username": test_user.email,
        "password": "password123"
    }
    login_response = client.post("/api/v1/auth/login", data=login_data)
    token = login_response.json()["access_token"]
    
    # Use token to get current user
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["email"] == test_user.email
    assert data["full_name"] == test_user.full_name
