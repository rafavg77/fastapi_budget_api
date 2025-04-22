import pytest
from fastapi import status
import json
import re
from src.main import app
from tests.security.utils import SecurityTestClient

@pytest.fixture
def security_client():
    return SecurityTestClient(app)

def test_cors_configuration(security_client, test_db):
    # Test CORS preflight request
    response = security_client.options(
        "/api/v1/users/",
        headers={
            "Origin": "http://malicious-site.com",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type",
        }
    )
    
    # Verify CORS headers
    assert "Access-Control-Allow-Origin" not in response.headers
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_security_headers(security_client, test_db):
    response = security_client.get("/")
    
    # Verify security headers are present and correct
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["X-XSS-Protection"] == "1; mode=block"
    assert response.headers["Strict-Transport-Security"] == "max-age=31536000; includeSubDomains"
    assert response.headers["Content-Security-Policy"] == "default-src 'self'"
    assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert response.headers["Cache-Control"] == "no-store, max-age=0"

def test_error_responses(security_client, test_db):
    # Test invalid JSON
    response = security_client.post(
        "/api/v1/users/",
        headers={"Content-Type": "application/json"},
        data="{invalid json}"
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    data = response.json()
    assert "detail" in data
    assert "Validation error" in data["detail"]
    assert not any(word in str(data).lower() for word in ["exception", "traceback"])

def test_secure_headers_in_responses(security_client, test_db):
    # Create a user and get token
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
    
    # Test various endpoints for secure headers
    endpoints = [
        "/api/v1/users/me/",
        "/api/v1/cards/",
        "/api/v1/",
        "/health"
    ]
    
    for endpoint in endpoints:
        response = security_client.get(
            endpoint,
            headers={"Authorization": f"Bearer {token}"} if "users" in endpoint or "cards" in endpoint else None
        )
        
        # Verify security headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["Cache-Control"] == "no-store, max-age=0"
        assert response.headers["X-Frame-Options"] == "DENY"

def test_debug_mode_disabled(security_client, test_db):
    # Test error endpoint to verify debug info is not exposed
    response = security_client.get("/nonexistent")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    
    # Verify no debug information is exposed
    assert "detail" in data
    assert not any(key in data for key in ["traceback", "debug", "stack"])