import docker
import logging
import json
import os
import sys
from datetime import datetime, timedelta

# Add Pro repo to path
PRO_PATH = "/home/ruser/containerguard-pro"
if PRO_PATH not in sys.path:
    sys.path.insert(0, PRO_PATH)

# Import license check
from license import check_license

# Import SlackAlert from Pro repo (renamed module)
try:
    from pro_agent.slack import SlackAlert
    SLACK_AVAILABLE = True
except ImportError:
    SLACK_AVAILABLE = False

logger = logging.getLogger(__name__)

class ContainerActions:
    def __init__(self, client):
        self.client = client
        self.history_file = "/tmp/containerguard_history.json"
        self.action_history = self._load_history()
        self.is_pro = check_license()
        
        # Initialize Slack if Pro
        self.slack = None
        if self.is_pro and SLACK_AVAILABLE:
            try:
                self.slack = SlackAlert()
                logger.info("✅ Pro features enabled: Slack alerts")
            except Exception as e:
                logger.warning(f"⚠️ Slack initialization failed: {e}")
        elif self.is_pro and not SLACK_AVAILABLE:
            logger.warning("⚠️ Pro features not available: No module named 'pro_agent.slack'")
        else:
            logger.info("ℹ️ Free tier: 7-day history limit, no Slack alerts")

    def _load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []

    def _trim_history(self, history):
        if self.is_pro:
            return history
        cutoff = datetime.now() - timedelta(days=7)
        trimmed = []
        for entry in history:
            try:
                entry_time = datetime.fromisoformat(entry['timestamp'])
                if entry_time > cutoff:
                    trimmed.append(entry)
            except (KeyError, ValueError):
                trimmed.append(entry)
        return trimmed

    def _save_history(self):
        try:
            self.action_history = self._trim_history(self.action_history)
            with open(self.history_file, 'w') as f:
                json.dump(self.action_history, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save history: {e}")

    def restart_container(self, container_id):
        try:
            container = self.client.containers.get(container_id)
            container.start()
            logger.info(f"✅ Restarted container: {container.name}")
            self.action_history.append({
                'timestamp': datetime.now().isoformat(),
                'action': 'restart',
                'container': container.name,
                'status': 'success'
            })
            self._save_history()
            if self.is_pro and self.slack:
                self.slack.send_alert(container.name, "restarted", "success")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to restart {container_id}: {e}")
            self.action_history.append({
                'timestamp': datetime.now().isoformat(),
                'action': 'restart',
                'container': str(container_id),
                'status': 'failed',
                'error': str(e)
            })
            self._save_history()
            return False

    def get_history(self):
        return self.action_history

    def cleanup_exited_containers(self):
        try:
            exited = self.client.containers.list(all=True, filters={'status': 'exited'})
            removed = []
            for container in exited:
                container.remove()
                removed.append(container.name)
                logger.info(f"🗑️ Removed exited container: {container.name}")
            if removed:
                self.action_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'action': 'cleanup',
                    'containers': removed,
                    'status': 'success'
                })
                self._save_history()
            return removed
        except Exception as e:
            logger.error(f"❌ Cleanup failed: {e}")
            return []
