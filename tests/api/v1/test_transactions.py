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

@pytest.fixture
def test_card_id(client, auth_headers):
    response = client.post(
        "/api/v1/cards/",
        headers=auth_headers,
        json={
            "card_number": "1234567890123456",
            "card_name": "Test Card",
            "bank_name": "Test Bank"
        }
    )
    return response.json()["id"]

def test_create_transaction(client, auth_headers, test_card_id):
    response = client.post(
        f"/api/v1/cards/{test_card_id}/transactions/",
        headers=auth_headers,
        json={
            "amount": 100.50,
            "description": "Test Transaction",
            "type": "income"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["amount"] == 100.50
    assert data["description"] == "Test Transaction"
    assert data["type"] == "income"
    assert data["card_id"] == test_card_id

def test_get_card_transactions(client, auth_headers, test_card_id):
    # Create a transaction first
    client.post(
        f"/api/v1/cards/{test_card_id}/transactions/",
        headers=auth_headers,
        json={
            "amount": 100.50,
            "description": "Test Transaction",
            "type": "income"
        }
    )
    
    response = client.get(
        f"/api/v1/cards/{test_card_id}/transactions/",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) > 0
    assert data[0]["amount"] == 100.50
    assert data[0]["description"] == "Test Transaction"

def test_delete_transaction(client, auth_headers, test_card_id):
    # Create a transaction first
    create_response = client.post(
        f"/api/v1/cards/{test_card_id}/transactions/",
        headers=auth_headers,
        json={
            "amount": 100.50,
            "description": "Test Transaction",
            "type": "income"
        }
    )
    transaction_id = create_response.json()["id"]
    
    # Delete the transaction
    response = client.delete(
        f"/api/v1/transactions/{transaction_id}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    
    # Verify transaction is deleted by checking card transactions
    get_response = client.get(
        f"/api/v1/cards/{test_card_id}/transactions/",
        headers=auth_headers
    )
    transactions = get_response.json()
    assert len(transactions) == 0

def test_create_transaction_invalid_card(client, auth_headers):
    response = client.post(
        "/api/v1/cards/999/transactions/",
        headers=auth_headers,
        json={
            "amount": 100.50,
            "description": "Test Transaction",
            "type": "income"
        }
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND