import time
import logging
import sys
from core import ContainerGuardAgent

# Setup logging to both console and file
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("/var/log/containerguard.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
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
            results = agent.run_once()
            logger.info("✅ Monitoring cycle completed")
            time.sleep(30)
        except KeyboardInterrupt:
            logger.info("🛑 Agent stopped by user")
            break
        except Exception as e:
            logger.error(f"❌ Error in monitoring cycle: {e}")
            time.sleep(30)

if __name__ == "__main__":
    main()
