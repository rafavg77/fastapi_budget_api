import pytest
from fastapi import status

def test_mass_assignment_vulnerability(client, test_db):
    # Create a user
    client.post(
        "/api/v1/users/",
        json={
            "email": "test@example.com",
            "password": "securepassword123",
            "full_name": "Test User"
        }
    )
    
    # Login
    login_response = client.post(
        "/api/v1/token",
        data={
            "username": "test@example.com",
            "password": "securepassword123"
        }
    )
    token = login_response.json()["access_token"]
    
    # Try to create a card with additional unauthorized fields
    response = client.post(
        "/api/v1/cards/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "card_number": "1234567890123456",
            "card_name": "Test Card",
            "bank_name": "Test Bank",
            "owner_id": 999,  # Trying to assign to a different user
            "is_admin": True,  # Trying to add unauthorized field
            "balance": 1000000  # Trying to add unauthorized field
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    # Verify that unauthorized fields were not assigned
    assert "is_admin" not in data
    assert "balance" not in data
    assert data["owner_id"] != 999

def test_excessive_data_exposure(client, test_db):
    # Create a user
    client.post(
        "/api/v1/users/",
        json={
            "email": "test@example.com",
            "password": "securepassword123",
            "full_name": "Test User"
        }
    )
    
    # Login
    login_response = client.post(
        "/api/v1/token",
        data={
            "username": "test@example.com",
            "password": "securepassword123"
        }
    )
    token = login_response.json()["access_token"]
    
    # Create a card
    card_response = client.post(
        "/api/v1/cards/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "card_number": "1234567890123456",
            "card_name": "Test Card",
            "bank_name": "Test Bank"
        }
    )
    card_id = card_response.json()["id"]
    
    # Get card details
    response = client.get(
        f"/api/v1/cards/{card_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    # Verify that sensitive data is not exposed
    assert "card_number" in data
    assert len(data["card_number"]) >= 4
    assert data["card_number"].startswith("*" * (len(data["card_number"]) - 4))

def test_sensitive_data_in_error_messages(client, test_db):
    # Try to create user with duplicate email
    client.post(
        "/api/v1/users/",
        json={
            "email": "test@example.com",
            "password": "securepassword123",
            "full_name": "Test User"
        }
    )
    
    response = client.post(
        "/api/v1/users/",
        json={
            "email": "test@example.com",
            "password": "differentpassword123",
            "full_name": "Another User"
        }
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    # Verify error message doesn't expose sensitive details
    assert "password" not in str(data)
    assert "hash" not in str(data)
    assert "salt" not in str(data)