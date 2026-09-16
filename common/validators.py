from typing import Dict, Any, Tuple, Optional
import re
from datetime import datetime

def validate_event(event_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """Validate event data"""
    required_fields = ['event_id', 'source', 'destination', 'event_type']
    
    for field in required_fields:
        if field not in event_data:
            return False, f"Missing required field: {field}"
    
    # Validate event_id format
    if not event_data['event_id'].startswith('EVT-'):
        return False, "Event ID must start with EVT-"
    
    # Validate timestamp if present
    if 'timestamp' in event_data:
        if isinstance(event_data['timestamp'], str):
            try:
                datetime.fromisoformat(event_data['timestamp'].replace('Z', '+00:00'))
            except ValueError:
                return False, "Invalid timestamp format"
    
    return True, None

def validate_alert(alert_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """Validate alert data"""
    required_fields = ['alert_id', 'severity', 'risk_score', 'attack_type']
    
    for field in required_fields:
        if field not in alert_data:
            return False, f"Missing required field: {field}"
    
    # Validate alert_id format
    if not alert_data['alert_id'].startswith('ALT-'):
        return False, "Alert ID must start with ALT-"
    
    # Validate risk_score range
    if 'risk_score' in alert_data:
        if not 0 <= alert_data['risk_score'] <= 100:
            return False, "Risk score must be between 0 and 100"
    
    # Validate confidence range
    if 'confidence' in alert_data:
        if not 0 <= alert_data['confidence'] <= 1:
            return False, "Confidence must be between 0 and 1"
    
    # Validate severity
    valid_severities = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO']
    if alert_data['severity'] not in valid_severities:
        return False, f"Invalid severity. Must be one of: {valid_severities}"
    
    return True, None

def validate_user(user_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """Validate user data"""
    required_fields = ['user_id', 'username', 'email', 'password_hash']
    
    for field in required_fields:
        if field not in user_data:
            return False, f"Missing required field: {field}"
    
    # Validate username
    if not re.match(r'^[a-zA-Z0-9_-]{3,50}$', user_data['username']):
        return False, "Username must be 3-50 characters and contain only alphanumeric, underscore, hyphen"
    
    # Validate email
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', user_data['email']):
        return False, "Invalid email format"
    
    # Validate role
    valid_roles = ['ADMIN', 'ANALYST', 'VIEWER']
    if 'role' in user_data and user_data['role'] not in valid_roles:
        return False, f"Invalid role. Must be one of: {valid_roles}"
    
    return True, None

def validate_incident(incident_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """Validate incident data"""
    required_fields = ['incident_id', 'title', 'description', 'severity']
    
    for field in required_fields:
        if field not in incident_data:
            return False, f"Missing required field: {field}"
    
    # Validate incident_id format
    if not incident_data['incident_id'].startswith('INC-'):
        return False, "Incident ID must start with INC-"
    
    # Validate status if present
    if 'status' in incident_data:
        valid_statuses = ['NEW', 'UNDER_INVESTIGATION', 'CONFIRMED', 'FALSE_POSITIVE', 
                         'CONTAINED', 'ERADICATED', 'RECOVERED', 'CLOSED']
        if incident_data['status'] not in valid_statuses:
            return False, f"Invalid status. Must be one of: {valid_statuses}"
    
    return True, None