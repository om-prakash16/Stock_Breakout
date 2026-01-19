import asyncio
import logging
from src.analytics.service import BreakoutService

logger = logging.getLogger(__name__)

async def run_scanner_loop():
    """
    Background task to periodically run the breakout scanner.
    """
    service = BreakoutService()
    while True:
        try:
            logger.info("Starting scheduled breakout scan...")
            print("Scheduler: Starting breakout scan...")
            # Run the blocking scan_universe method in a separate thread
            await asyncio.to_thread(service.scan_universe)
            print("Scheduler: Scan complete. Sleeping for 5 minutes.")
        except Exception as e:
            logger.error(f"Scheduler Error: {e}")
            print(f"Scheduler Error: {e}")
            
        # Sleep for 5 minutes (300 seconds)
        await asyncio.sleep(300)

def start_scheduler():
    """
    Starts the background scheduler task.
    """
    asyncio.create_task(run_scanner_loop())
