from fastapi.testclient import TestClient
from typing import List, Dict, Any
from datetime import datetime
import logging
from collections import defaultdict

# Mock storage for audit logs and alerts in testing environment
_audit_logs = []
_security_alerts = defaultdict(list)

def get_audit_logs() -> List[Dict[str, Any]]:
    """Get all audit logs collected during testing"""
    return _audit_logs

def get_security_alerts(start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
    """Get security alerts generated between start_time and end_time"""
    return [
        alert for alert in _security_alerts[start_time.date()]
        if start_time <= alert["timestamp"] <= end_time
    ]

class SecurityTestClient(TestClient):
    """Extended TestClient with security testing capabilities"""
    
    def __init__(self, app, **kwargs):
        super().__init__(app, **kwargs)
        self.request_count = defaultdict(int)
        self.last_request_time = defaultdict(float)
    
    def _record_audit(self, method: str, url: str, status_code: int, user_id: str = None):
        """Record an audit log entry"""
        _audit_logs.append({
            "timestamp": datetime.now(),
            "user_id": user_id,
            "action": method,
            "resource": url,
            "status": status_code,
            "request_id": "test-" + str(len(_audit_logs) + 1)
        })
    
    def _check_rate_limit(self, key: str, threshold: int = 100, window: int = 60) -> bool:
        """Check if rate limit is exceeded"""
        current_time = datetime.now().timestamp()
        if current_time - self.last_request_time[key] > window:
            self.request_count[key] = 0
            
        self.request_count[key] += 1
        self.last_request_time[key] = current_time
        
        if self.request_count[key] > threshold:
            _security_alerts[datetime.now().date()].append({
                "timestamp": datetime.now(),
                "alert_type": "RATE_LIMIT_EXCEEDED",
                "severity": "HIGH",
                "details": f"Rate limit exceeded for {key}",
                "threshold": threshold,
                "current_value": self.request_count[key],
                "source_ip": "127.0.0.1"
            })
            return True
        return False

    def request(self, method: str, url: str, **kwargs) -> TestClient:
        """Override request method to add security monitoring"""
        response = super().request(method, url, **kwargs)
        self._record_audit(method, url, response.status_code)
        self._check_rate_limit(f"{method}:{url}")
        return response