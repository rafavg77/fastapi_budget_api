import pytest
import logging
from datetime import datetime, timedelta
from src.main import app
from src.app.core.monitoring import get_security_alerts
from tests.security.utils import SecurityTestClient
from fastapi.testclient import TestClient

@pytest.fixture
def security_client():
    return SecurityTestClient(app)

def test_log_format_and_content(caplog, client, test_db):
    caplog.set_level(logging.INFO)
    
    # Test successful login
    response = client.post(
        "/api/v1/users/",
        json={
            "email": "test@example.com",
            "password": "SecurePass123!",
            "full_name": "Test User"
        }
    )
    
    # Check log format
    for record in caplog.records:
        assert hasattr(record, 'asctime')
        assert hasattr(record, 'levelname')
        assert hasattr(record, 'message')
        if hasattr(record, 'extra') and record.extra.get('security'):
            assert 'event_type' in record.extra

def test_security_events_logging(caplog, client, test_db):
    caplog.set_level(logging.WARNING)
    
    # Test failed login attempts
    for _ in range(5):
        client.post(
            "/api/v1/token",
            data={
                "username": "test@example.com",
                "password": "wrongpassword"
            }
        )
    
    # Verify security events are logged
    security_logs = [
        record for record in caplog.records
        if record.levelname in ['WARNING', 'ERROR']
        and any(word in record.message.lower() for word in ['security', 'failed', 'attempt'])
    ]
    assert len(security_logs) > 0

def test_audit_trail(client, test_db):
    # Create test user
    start_time = datetime.now()
    
    client.post(
        "/api/v1/users/",
        json={
            "email": "test@example.com",
            "password": "SecurePass123!",
            "full_name": "Test User"
        }
    )
    
    # Login
    login_response = client.post(
        "/api/v1/token",
        data={
            "username": "test@example.com",
            "password": "SecurePass123!"
        }
    )
    token = login_response.json()["access_token"]
    
    # Perform some actions
    client.get(
        "/api/v1/users/me/",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    end_time = datetime.now()
    
    # Check audit trail
    alerts = get_security_alerts(start_time, end_time)
    assert any(alert.event_type == "user_created" for alert in alerts)
    assert any(alert.event_type == "user_login" for alert in alerts)

def test_monitoring_alerts(client, test_db):
    # Test rate limit alerts
    start_time = datetime.now()
    
    # Generate suspicious activity
    for _ in range(100):
        client.post(
            "/api/v1/token",
            data={
                "username": "nonexistent@example.com",
                "password": "wrongpassword"
            }
        )
    
    end_time = datetime.now() + timedelta(seconds=1)
    
    # Check security alerts
    alerts = get_security_alerts(start_time, end_time)
    assert len(alerts) > 0
    assert any(alert.event_type == "rate_limit_exceeded" for alert in alerts)