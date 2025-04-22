import pytest
from fastapi import status
from src.main import app
from tests.security.utils import SecurityTestClient
import re

@pytest.fixture
def security_client():
    return SecurityTestClient(app)

def test_api_versioning(client, test_db):
    # Test current API version
    response = client.get("/api/v1/")
    assert response.status_code == status.HTTP_200_OK
    
    # Test non-existent version
    response = client.get("/api/v2/")
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_api_documentation(client, test_db):
    # Test OpenAPI documentation availability
    response = client.get("/openapi.json")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    # Verify API documentation completeness
    assert "paths" in data
    assert "components" in data
    assert "schemas" in data
    
    # Check security definitions
    assert "security" in data
    assert "securitySchemes" in data.get("components", {})

def test_deprecated_endpoints(client, test_db):
    # Create user and get token
    client.post(
        "/api/v1/users/",
        json={
            "email": "test@example.com",
            "password": "securepassword123",
            "full_name": "Test User"
        }
    )
    
    login_response = client.post(
        "/api/v1/token",
        data={
            "username": "test@example.com",
            "password": "securepassword123"
        }
    )
    token = login_response.json()["access_token"]
    
    # Test deprecated endpoints
    deprecated_endpoints = [
        "/api/v1/deprecated/",
        "/api/v1/old-endpoint/"
    ]
    
    for endpoint in deprecated_endpoints:
        response = client.get(
            endpoint,
            headers={"Authorization": f"Bearer {token}"}
        )
        # Should either return 410 Gone or include deprecation warning header
        assert response.status_code in [status.HTTP_410_GONE, status.HTTP_200_OK]
        if response.status_code == status.HTTP_200_OK:
            assert "Warning" in response.headers
            assert "deprecated" in response.headers["Warning"].lower()

def test_health_and_monitoring_endpoints(client, test_db):
    # Test health check endpoint
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"
    
    # Test metrics endpoint
    response = client.get("/metrics")
    assert response.status_code == status.HTTP_200_OK
    content = response.text
    
    # Check for common metric patterns
    assert re.search(r'http_requests_total\{[^}]+\} \d+', content)
    assert re.search(r'http_request_duration_seconds\{[^}]+\} \d+\.\d+', content)