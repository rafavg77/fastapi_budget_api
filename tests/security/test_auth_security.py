import pytest
from fastapi import status
import logging

logger = logging.getLogger(__name__)

def test_broken_object_level_authorization(client, test_db):
    # Create two users
    user1_response = client.post(
        "/api/v1/users/",
        json={
            "email": "user1@example.com",
            "password": "password123",
            "full_name": "User One"
        }
    )
    user2_response = client.post(
        "/api/v1/users/",
        json={
            "email": "user2@example.com",
            "password": "password123",
            "full_name": "User Two"
        }
    )

    # Login as user1
    login1_response = client.post(
        "/api/v1/token",
        data={
            "username": "user1@example.com",
            "password": "password123"
        }
    )
    user1_token = login1_response.json()["access_token"]

    # Create a card for user1
    card_response = client.post(
        "/api/v1/cards/",
        headers={"Authorization": f"Bearer {user1_token}"},
        json={
            "card_number": "1234567890123456",
            "card_name": "Test Card",
            "bank_name": "Test Bank"
        }
    )
    card_id = card_response.json()["id"]

    # Login as user2
    login2_response = client.post(
        "/api/v1/token",
        data={
            "username": "user2@example.com",
            "password": "password123"
        }
    )
    user2_token = login2_response.json()["access_token"]

    # Try to access user1's card with user2's token
    response = client.get(
        f"/api/v1/cards/{card_id}",
        headers={"Authorization": f"Bearer {user2_token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_broken_authentication(client, test_db):
    # Test with expired token
    expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGV4YW1wbGUuY29tIiwiZXhwIjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    response = client.get(
        "/api/v1/users/me/",
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # Test with invalid token format
    response = client.get(
        "/api/v1/users/me/",
        headers={"Authorization": "InvalidToken"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # Test with missing token
    response = client.get("/api/v1/users/me/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_create_user(security_client, test_db):
    """Test user creation with proper password requirements."""
    response = security_client.post(
        "/api/v1/users/",
        json={
            "email": "test@example.com",
            "password": "SecurePass123!",  # Meets complexity requirements
            "full_name": "Test User"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    
def test_weak_password(security_client, test_db):
    """Test rejection of weak passwords."""
    response = security_client.post(
        "/api/v1/users/",
        json={
            "email": "test@example.com",
            "password": "weak",  # Does not meet complexity requirements
            "full_name": "Test User"
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    
def test_brute_force_protection(security_client, test_db):
    """Test protection against brute force attacks."""
    # Create a user first
    security_client.post(
        "/api/v1/users/",
        json={
            "email": "test@example.com",
            "password": "SecurePass123!",
            "full_name": "Test User"
        }
    )
    
    # Attempt multiple failed logins
    for _ in range(6):
        response = security_client.post(
            "/api/v1/token",
            data={
                "username": "test@example.com",
                "password": "wrongpassword"
            }
        )
    
    # Should be blocked now
    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    
def test_password_hashing(security_client, test_db):
    """Test that passwords are properly hashed."""
    # Create user
    response = security_client.post(
        "/api/v1/users/",
        json={
            "email": "test@example.com",
            "password": "SecurePass123!",
            "full_name": "Test User"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    
    # Try to login with correct password
    response = security_client.post(
        "/api/v1/token",
        data={
            "username": "test@example.com",
            "password": "SecurePass123!"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()

def test_session_management(security_client, test_db):
    """Test proper session management with JWT tokens."""
    # Create user and get token
    security_client.post(
        "/api/v1/users/",
        json={
            "email": "test@example.com",
            "password": "SecurePass123!",
            "full_name": "Test User"
        }
    )
    
    login_response = security_client.post(
        "/api/v1/token",
        data={
            "username": "test@example.com",
            "password": "SecurePass123!"
        }
    )
    token = login_response.json()["access_token"]
    
    # Test protected endpoint with token
    response = security_client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    
    # Test with invalid token
    response = security_client.get(
        "/api/v1/users/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED