"""
ContainerGuard Agent - Core Monitoring Module
Now with auto-healing capabilities
"""

import docker
import logging
import time
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.actions import ContainerActions

# Setup logging
logging.basicConfig(handlers=[logging.FileHandler("/var/log/containerguard.log"), logging.StreamHandler()], 
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ContainerGuardAgent:
    """Main agent class with auto-healing"""
    
    def __init__(self, docker_host='tcp://192.168.217.163:2375'):
        try:
            self.client = docker.DockerClient(base_url=docker_host)
            self.actions = ContainerActions(self.client)
            logger.info(f"✅ Connected to Docker at {docker_host}")
        except Exception as e:
            logger.error(f"❌ Failed to connect: {e}")
            raise
    
    def get_all_containers(self):
        try:
            containers = self.client.containers.list(all=True)
            logger.info(f"Found {len(containers)} containers")
            return containers
        except Exception as e:
            logger.error(f"Error listing containers: {e}")
            return []
    
    def check_and_heal(self):
        """Check health and auto-restart exited containers"""
        containers = self.get_all_containers()
        status_report = []
        restarted_count = 0
        
        for container in containers:
            status = container.status
            name = container.name
            
            # Auto-heal: restart exited containers
            if status == 'exited':
                logger.warning(f"⚠️ {name}: EXITED - Attempting restart...")
                if self.actions.restart_container(container.id):
                    restarted_count += 1
                    status = 'restarted'
                else:
                    status = 'exited_failed'
            
            elif status == 'running':
                logger.info(f"✅ {name}: RUNNING")
            
            else:
                logger.info(f"ℹ️ {name}: {status}")
            
            status_report.append({'name': name, 'status': status})
        
        if restarted_count > 0:
            logger.info(f"🔄 Auto-restarted {restarted_count} container(s)")
        
        return status_report, restarted_count
    
    def run_once(self):
        """Run a single monitoring + healing cycle"""
        logger.info("🔍 Starting monitoring + healing cycle...")
        results, restarted = self.check_and_heal()
        logger.info(f"📊 Monitored {len(results)} containers, restarted {restarted}")
        return results

if __name__ == "__main__":
    logger.info("🚀 ContainerGuard Agent - Auto-Heal Mode")
    agent = ContainerGuardAgent()
    results = agent.run_once()
    
    print("\n📋 Container Status Summary:")
    for r in results:
        status_icon = "🔄" if r['status'] == 'restarted' else ("⚠️" if r['status'] == 'exited_failed' else "✅")
        print(f"  {status_icon} {r['name']}: {r['status']}")
    
    # Show action history
    history = agent.actions.get_history()
    if history:
        print("\n📜 Action History:")
        for action in history:
            print(f"  {action['timestamp']} - {action['action']} {action['container']} - {action['status']}")
