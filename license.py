"""
ContainerGuard License Module
Handles free vs pro tier detection
"""

import os
import json
import logging

logger = logging.getLogger(__name__)

LICENSE_FILE = "/etc/containerguard/license.json"

def get_license():
    """Get license information from file"""
    if os.path.exists(LICENSE_FILE):
        try:
            with open(LICENSE_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load license: {e}")
    return {"tier": "free"}

def is_pro():
    """Check if user has Pro tier"""
    license = get_license()
    return license.get("tier") == "pro"

def get_tier():
    """Get current tier"""
    return get_license().get("tier", "free")

def get_history_days():
    """Get number of days to keep history"""
    if is_pro():
        return 0  # Unlimited (0 means no limit)
    return 7  # Free tier: 7 days

def get_features():
    """Get features available for current tier"""
    tier = get_tier()
    if tier == "pro":
        return {
            "history_days": 0,
            "slack_alerts": True,
            "auto_cleanup": True,
            "multi_host": True
        }
    return {
        "history_days": 7,
        "slack_alerts": False,
        "auto_cleanup": False,
        "multi_host": False
    }
