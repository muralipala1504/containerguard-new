import docker
import logging
import json
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class ContainerActions:
    def __init__(self, client):
        self.client = client
        self.history_file = "/tmp/containerguard_history.json"
        self.action_history = self._load_history()

    def _load_history(self):
        """Load history from file"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []

    def _save_history(self):
        """Save history to file"""
        try:
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
