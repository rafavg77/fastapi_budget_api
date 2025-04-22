import pytest
from fastapi import status

@pytest.fixture
def auth_headers(client):
    # Create user and get token
    client.post(
        "/api/v1/users/",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User"
        }
    )
    
    response = client.post(
        "/api/v1/token",
        data={
            "username": "test@example.com",
            "password": "testpassword123"
        }
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_create_card(client, auth_headers):
    response = client.post(
        "/api/v1/cards/",
        headers=auth_headers,
        json={
            "card_number": "1234567890123456",
            "card_name": "Test Card",
            "bank_name": "Test Bank"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["card_number"] == "1234567890123456"
    assert data["card_name"] == "Test Card"
    assert data["bank_name"] == "Test Bank"
    assert "id" in data
    assert "owner_id" in data

def test_get_user_cards(client, auth_headers):
    # Create a card first
    client.post(
        "/api/v1/cards/",
        headers=auth_headers,
        json={
            "card_number": "1234567890123456",
            "card_name": "Test Card",
            "bank_name": "Test Bank"
        }
    )
    
    response = client.get("/api/v1/cards/", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) > 0
    assert data[0]["card_name"] == "Test Card"

def test_get_card_by_id(client, auth_headers):
    # Create a card first
    create_response = client.post(
        "/api/v1/cards/",
        headers=auth_headers,
        json={
            "card_number": "1234567890123456",
            "card_name": "Test Card",
            "bank_name": "Test Bank"
        }
    )
    card_id = create_response.json()["id"]
    
    response = client.get(f"/api/v1/cards/{card_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == card_id
    assert data["card_name"] == "Test Card"

def test_delete_card(client, auth_headers):
    # Create a card first
    create_response = client.post(
        "/api/v1/cards/",
        headers=auth_headers,
        json={
            "card_number": "1234567890123456",
            "card_name": "Test Card",
            "bank_name": "Test Bank"
        }
    )
    card_id = create_response.json()["id"]
    
    # Delete the card
    response = client.delete(f"/api/v1/cards/{card_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    
    # Verify card is deleted
    get_response = client.get(f"/api/v1/cards/{card_id}", headers=auth_headers)
    assert get_response.status_code == status.HTTP_404_NOT_FOUND