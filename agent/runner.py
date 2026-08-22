"""
ContainerGuard Agent - Continuous Runner
Runs the agent in an infinite loop with configurable interval
"""

import time
import logging
import sys
from core import ContainerGuardAgent

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/containerguard.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Main loop - runs agent every 30 seconds"""
    logger.info("🚀 ContainerGuard Agent - Continuous Mode Started")
    logger.info("⏱️  Monitoring interval: 30 seconds")
    
    try:
        agent = ContainerGuardAgent()
    except Exception as e:
        logger.error(f"❌ Failed to initialize agent: {e}")
        sys.exit(1)
    
    cycle_count = 0
    
    while True:
        try:
            cycle_count += 1
            logger.info(f"🔄 Cycle {cycle_count} starting...")
            
            # Run monitoring + healing
            results = agent.run_once()
            
            # Summary
            exited = [r for r in results if r['status'] == 'exited' or r['status'] == 'exited_failed']
            if exited:
                logger.warning(f"⚠️ {len(exited)} containers still have issues: {[r['name'] for r in exited]}")
            else:
                logger.info("✅ All containers healthy")
            
            # Show recent action history (last action only)
            history = agent.actions.get_history()
            if history:
                last_action = history[-1]
                logger.info(f"📜 Last action: {last_action['action']} {last_action['container']} - {last_action['status']}")
            
            # Wait before next cycle
            logger.info(f"⏳ Waiting 30 seconds...")
            time.sleep(30)
            
        except KeyboardInterrupt:
            logger.info("🛑 Agent stopped by user")
            break
        except Exception as e:
            logger.error(f"❌ Error in monitoring cycle: {e}")
            logger.info("⏳ Waiting 30 seconds before retry...")
            time.sleep(30)

if __name__ == "__main__":
    main()
