"""
ContainerGuard Audit Logs
Tracks all user actions for compliance and debugging
"""

import os
import json
from datetime import datetime

AUDIT_FILE = "/tmp/containerguard_audit.json"

def log_action(user, action, resource, details, status="success"):
    """Log an action to the audit file"""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "user": user,
        "action": action,
        "resource": resource,
        "details": details,
        "status": status
    }
    
    # Load existing logs
    logs = []
    if os.path.exists(AUDIT_FILE):
        try:
            with open(AUDIT_FILE, 'r') as f:
                logs = json.load(f)
        except:
            pass
    
    # Add new entry
    logs.append(entry)
    
    # Keep last 1000 entries
    if len(logs) > 1000:
        logs = logs[-1000:]
    
    # Save to file
    with open(AUDIT_FILE, 'w') as f:
        json.dump(logs, f, indent=2)
    
    return entry

def get_audit_logs(limit=50):
    """Get recent audit logs"""
    if os.path.exists(AUDIT_FILE):
        try:
            with open(AUDIT_FILE, 'r') as f:
                logs = json.load(f)
                return logs[-limit:] if len(logs) > limit else logs
        except:
            return []
    return []

def get_audit_logs_by_user(user, limit=50):
    """Get audit logs for a specific user"""
    logs = get_audit_logs(1000)
    user_logs = [l for l in logs if l.get('user') == user]
    return user_logs[-limit:] if len(user_logs) > limit else user_logs

def export_audit_logs():
    """Export all audit logs as JSON"""
    logs = get_audit_logs(10000)
    return json.dumps(logs, indent=2)
