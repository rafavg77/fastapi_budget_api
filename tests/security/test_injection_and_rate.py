import pytest
from fastapi import status
import time
from src.main import app
from tests.security.utils import SecurityTestClient

@pytest.fixture
def security_client():
    return SecurityTestClient(app)

def test_sql_injection_prevention(security_client, test_db):
    # Test SQL injection in login
    response = security_client.post(
        "/api/v1/token",
        data={
            "username": "' OR '1'='1",
            "password": "' OR '1'='1"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # Test SQL injection in email parameter
    response = security_client.post(
        "/api/v1/users/",
        json={
            "email": "test@example.com'; DROP TABLE users; --",
            "password": "securepassword123",
            "full_name": "Test User"
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Test SQL injection in card search
    user_response = security_client.post(
        "/api/v1/users/",
        json={
            "email": "test@example.com",
            "password": "securepassword123",
            "full_name": "Test User"
        }
    )
    
    login_response = security_client.post(
        "/api/v1/token",
        data={
            "username": "test@example.com",
            "password": "securepassword123"
        }
    )
    token = login_response.json()["access_token"]
    
    # Try SQL injection in query parameter
    response = security_client.get(
        "/api/v1/cards/?card_number=' OR '1'='1",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_rate_limiting(security_client, test_db):
    # Create test user
    security_client.post(
        "/api/v1/users/",
        json={
            "email": "test@example.com",
            "password": "securepassword123",
            "full_name": "Test User"
        }
    )
    
    # Test rate limiting on login endpoint
    start_time = time.time()
    responses = []
    
    for _ in range(50):  # Number of requests to test
        response = security_client.post(
            "/api/v1/token",
            data={
                "username": "test@example.com",
                "password": "wrongpassword"
            }
        )
        responses.append(response.status_code)
        if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            break
    
    end_time = time.time()
    time_elapsed = end_time - start_time
    
    # Verify that rate limiting was applied
    assert status.HTTP_429_TOO_MANY_REQUESTS in responses
    assert time_elapsed < 60  # Test should complete within reasonable time

def test_brute_force_protection(security_client, test_db):
    # Create test user
    security_client.post(
        "/api/v1/users/",
        json={
            "email": "test@example.com",
            "password": "securepassword123",
            "full_name": "Test User"
        }
    )
    
    # Try multiple failed login attempts
    for i in range(10):
        security_client.post(
            "/api/v1/token",
            data={
                "username": "test@example.com",
                "password": f"wrongpassword{i}"
            }
        )
    
    # Verify account is temporarily locked
    response = security_client.post(
        "/api/v1/token",
        data={
            "username": "test@example.com",
            "password": "securepassword123"  # Correct password
        }
    )
    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS