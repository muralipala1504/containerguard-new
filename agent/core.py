"""
ContainerGuard Agent - Core Monitoring Module
Connects to Docker API and monitors container health
"""

import docker
import logging
import time
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ContainerGuardAgent:
    """Main agent class for container monitoring"""
    
    def __init__(self, docker_host='tcp://192.168.217.163:2375'):
        """Initialize connection to Docker"""
        try:
            self.client = docker.DockerClient(base_url=docker_host)
            logger.info(f"✅ Connected to Docker at {docker_host}")
        except Exception as e:
            logger.error(f"❌ Failed to connect: {e}")
            raise
    
    def get_all_containers(self):
        """Get list of all containers (including stopped)"""
        try:
            containers = self.client.containers.list(all=True)
            logger.info(f"Found {len(containers)} containers")
            return containers
        except Exception as e:
            logger.error(f"Error listing containers: {e}")
            return []
    
    def check_health(self):
        """Check health status of all containers"""
        containers = self.get_all_containers()
        status_report = []
        
        for container in containers:
            status = container.status
            name = container.name
            
            if status == 'exited':
                logger.warning(f"⚠️ {name}: EXITED")
                status_report.append({'name': name, 'status': 'exited'})
            elif status == 'running':
                logger.info(f"✅ {name}: RUNNING")
                status_report.append({'name': name, 'status': 'running'})
            else:
                logger.info(f"ℹ️ {name}: {status}")
                status_report.append({'name': name, 'status': status})
        
        return status_report
    
    def run_once(self):
        """Run a single monitoring cycle"""
        logger.info("🔍 Starting monitoring cycle...")
        results = self.check_health()
        logger.info(f"📊 Monitored {len(results)} containers")
        return results

if __name__ == "__main__":
    # Quick test when run directly
    logger.info("🚀 ContainerGuard Agent - Test Mode")
    agent = ContainerGuardAgent()
    results = agent.run_once()
    
    print("\n📋 Container Status Summary:")
    for r in results:
        print(f"  - {r['name']}: {r['status']}")
