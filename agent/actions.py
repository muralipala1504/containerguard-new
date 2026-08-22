"""
ContainerGuard Agent - Auto Actions Module
Contains self-healing and cleanup operations
"""

import docker
import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)

class ContainerActions:
    """Actions that the agent can perform on containers"""
    
    def __init__(self, client):
        self.client = client
        self.action_history = []
    
    def restart_container(self, container_id):
        """Restart a container that has exited"""
        try:
            container = self.client.containers.get(container_id)
            container.start()
            logger.info(f"✅ Restarted container: {container.name}")
            
            # Log the action
            self.action_history.append({
                'timestamp': datetime.now().isoformat(),
                'action': 'restart',
                'container': container.name,
                'status': 'success'
            })
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to restart {container_id}: {e}")
            self.action_history.append({
                'timestamp': datetime.now().isoformat(),
                'action': 'restart',
                'container': container_id,
                'status': 'failed',
                'error': str(e)
            })
            return False
    
    def get_history(self):
        """Return action history"""
        return self.action_history
    
    def cleanup_exited_containers(self):
        """Remove exited containers (optional cleanup)"""
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
            return removed
            
        except Exception as e:
            logger.error(f"❌ Cleanup failed: {e}")
            return []
