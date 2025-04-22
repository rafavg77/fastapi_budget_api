import pytest
from fastapi import status

def test_create_user(client):
    response = client.post(
        "/api/v1/users/",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test User"
    assert "password" not in data
    assert "id" in data

def test_create_user_duplicate_email(client):
    # Create first user
    client.post(
        "/api/v1/users/",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User"
        }
    )
    
    # Try to create user with same email
    response = client.post(
        "/api/v1/users/",
        json={
            "email": "test@example.com",
            "password": "different_password",
            "full_name": "Different User"
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_login_user(client):
    # Create user first
    client.post(
        "/api/v1/users/",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User"
        }
    )
    
    # Try to login
    response = client.post(
        "/api/v1/token",
        data={
            "username": "test@example.com",
            "password": "testpassword123"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_user_wrong_password(client):
    # Create user first
    client.post(
        "/api/v1/users/",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User"
        }
    )
    
    # Try to login with wrong password
    response = client.post(
        "/api/v1/token",
        data={
            "username": "test@example.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_current_user(client):
    # Create user and get token
    client.post(
        "/api/v1/users/",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User"
        }
    )
    
    login_response = client.post(
        "/api/v1/token",
        data={
            "username": "test@example.com",
            "password": "testpassword123"
        }
    )
    token = login_response.json()["access_token"]
    
    # Get current user info
    response = client.get(
        "/api/v1/users/me/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test User"