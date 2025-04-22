from datetime import datetime, timedelta
import logging
from typing import List, Dict, Any, Optional
from collections import defaultdict
import threading
from dataclasses import dataclass
import json
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class SecurityAlert:
    timestamp: datetime
    event_type: str
    description: str
    severity: str
    source_ip: str | None = None

class SecurityMonitor:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(SecurityMonitor, cls).__new__(cls)
                    cls._instance.initialize()
        return cls._instance

    def initialize(self):
        self.alerts: List[SecurityAlert] = []
        self.failed_logins = defaultdict(list)
        self.request_counts = defaultdict(list)
        self.suspicious_activities = defaultdict(list)

    def add_alert(self, alert: SecurityAlert):
        with self._lock:
            self.alerts.append(alert)
            logger.warning(
                f"Security Alert: {alert.event_type} - {alert.description}",
                extra={
                    "security": True,
                    "event_type": alert.event_type,
                    "severity": alert.severity,
                    "source_ip": alert.source_ip
                }
            )

    def get_alerts(self, start_time: datetime, end_time: datetime) -> List[SecurityAlert]:
        with self._lock:
            return [
                alert for alert in self.alerts
                if start_time <= alert.timestamp <= end_time
            ]

    def record_failed_login(self, ip_address: str, timestamp: datetime = None):
        if timestamp is None:
            timestamp = datetime.now()
        
        with self._lock:
            self.failed_logins[ip_address].append(timestamp)
            recent_failures = [
                t for t in self.failed_logins[ip_address]
                if timestamp - t < timedelta(minutes=5)
            ]
            self.failed_logins[ip_address] = recent_failures

            if len(recent_failures) >= 5:
                self.add_alert(SecurityAlert(
                    timestamp=timestamp,
                    event_type="brute_force_attempt",
                    description=f"Multiple failed login attempts from {ip_address}",
                    severity="high",
                    source_ip=ip_address
                ))

    def record_request(self, ip_address: str, endpoint: str, timestamp: datetime = None):
        if timestamp is None:
            timestamp = datetime.now()
        
        with self._lock:
            self.request_counts[ip_address].append(timestamp)
            recent_requests = [
                t for t in self.request_counts[ip_address]
                if timestamp - t < timedelta(minutes=1)
            ]
            self.request_counts[ip_address] = recent_requests

            if len(recent_requests) > 100:
                self.add_alert(SecurityAlert(
                    timestamp=timestamp,
                    event_type="rate_limit_exceeded",
                    description=f"Rate limit exceeded for {ip_address}",
                    severity="medium",
                    source_ip=ip_address
                ))

    def record_suspicious_activity(self, ip_address: str, activity_type: str, details: str):
        timestamp = datetime.now()
        with self._lock:
            self.suspicious_activities[ip_address].append((timestamp, activity_type))
            self.add_alert(SecurityAlert(
                timestamp=timestamp,
                event_type="suspicious_activity",
                description=f"{activity_type}: {details}",
                severity="medium",
                source_ip=ip_address
            ))

# Global instance
security_monitor = SecurityMonitor()

# Initialize security event storage
SECURITY_EVENTS = []
AUDIT_LOG_PATH = Path("audit.log")

def record_security_event(
    event_type: str,
    description: str,
    severity: str = "low",
    source_ip: Optional[str] = None,
    user_id: Optional[str] = None
) -> None:
    """Record a security event for monitoring."""
    event = {
        "timestamp": datetime.utcnow().isoformat(),
        "type": event_type,
        "description": description,
        "severity": severity,
        "source_ip": source_ip,
        "user_id": user_id
    }
    
    SECURITY_EVENTS.append(event)
    
    # Log the security event
    log_level = {
        "low": logging.INFO,
        "medium": logging.WARNING,
        "high": logging.ERROR,
        "critical": logging.CRITICAL
    }.get(severity, logging.INFO)
    
    logger.log(log_level, f"Security Event: {json.dumps(event)}", extra={"security": True})
    
    # Write to audit log
    with AUDIT_LOG_PATH.open("a") as f:
        f.write(json.dumps(event) + "\n")

def get_security_alerts(start_time: datetime, end_time: datetime) -> list:
    """Get security alerts within a time range."""
    alerts = []
    for event in SECURITY_EVENTS:
        event_time = datetime.fromisoformat(event["timestamp"])
        if start_time <= event_time <= end_time:
            alerts.append(event)
    return alerts

def get_audit_trail(start_time: datetime, end_time: datetime) -> list:
    """Get audit trail entries within a time range."""
    if not AUDIT_LOG_PATH.exists():
        return []
        
    audit_entries = []
    with AUDIT_LOG_PATH.open("r") as f:
        for line in f:
            try:
                entry = json.loads(line)
                event_time = datetime.fromisoformat(entry["timestamp"])
                if start_time <= event_time <= end_time:
                    audit_entries.append(entry)
            except (json.JSONDecodeError, KeyError, ValueError):
                logger.error("Error parsing audit log entry", extra={"security": True})
                continue
    
    return audit_entries