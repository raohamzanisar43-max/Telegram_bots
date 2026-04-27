"""
main.py - Professional Single Entry Point for Profitability Intelligence Bots
Ready for Railway deployment with all three bots running concurrently.
"""
import asyncio
import logging
import os
import signal
import sys
from contextlib import asynccontextmanager
from typing import List

import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/main.log', encoding='utf-8') if os.path.exists('logs') else logging.NullHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global references to bot tasks
bot_tasks: List[asyncio.Task] = []


async def start_signals_bot():
    """Start the Signals Bot (ProfitFeedNewsBot)"""
    try:
        from signals_bot.main import main as signals_main
        
        # Create a new event loop for the signals bot
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        logger.info("🚀 Starting Signals Bot (@ProfitFeedNewsBot)")
        await signals_main()
        
    except Exception as e:
        logger.error(f"❌ Signals Bot failed to start: {e}")
        raise


async def start_copy_bot():
    """Start the Copy Bot (S2TCopyBot)"""
    try:
        from copy_bot.main import main as copy_main
        
        # Create a new event loop for the copy bot
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        logger.info("🚀 Starting Copy Bot (@S2TCopyBot)")
        await copy_main()
        
    except Exception as e:
        logger.error(f"❌ Copy Bot failed to start: {e}")
        raise


async def start_funded_bot():
    """Start the Funded Bot (FundedS2TBot)"""
    try:
        from funded_bot.main import main as funded_main
        
        # Create a new event loop for the funded bot
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        logger.info("🚀 Starting Funded Bot (@FundedS2TBot)")
        await funded_main()
        
    except Exception as e:
        logger.error(f"❌ Funded Bot failed to start: {e}")
        raise


async def start_admin_api():
    """Start the Admin API"""
    try:
        from admin.main import app
        
        logger.info("🚀 Starting Admin API on port 4000")
        
        # Configure uvicorn for Railway
        config = uvicorn.Config(
            app=app,
            host="0.0.0.0",  # Railway requires 0.0.0.0
            port=int(os.getenv("PORT", 4000)),
            log_level="info",
            access_log=True
        )
        
        server = uvicorn.Server(config)
        await server.serve()
        
    except Exception as e:
        logger.error(f"❌ Admin API failed to start: {e}")
        raise


async def start_all_services():
    """Start all services concurrently"""
    logger.info("🎯 Starting Profitability Intelligence - All Services")
    
    # Create tasks for all services
    tasks = [
        asyncio.create_task(start_admin_api(), name="admin-api"),
        asyncio.create_task(start_signals_bot(), name="signals-bot"),
        asyncio.create_task(start_copy_bot(), name="copy-bot"),
        asyncio.create_task(start_funded_bot(), name="funded-bot"),
    ]
    
    global bot_tasks
    bot_tasks = tasks
    
    try:
        # Wait for all tasks to complete (they should run indefinitely)
        await asyncio.gather(*tasks, return_exceptions=True)
    except Exception as e:
        logger.error(f"❌ Service startup failed: {e}")
        raise


def setup_signal_handlers():
    """Setup graceful shutdown handlers"""
    def signal_handler(signum, frame):
        logger.info(f"🛑 Received signal {signum}, shutting down gracefully...")
        for task in bot_tasks:
            if not task.done():
                task.cancel()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def main():
    """Main entry point"""
    # Ensure log directory exists
    os.makedirs("logs", exist_ok=True)
    
    # Setup signal handlers for graceful shutdown
    setup_signal_handlers()
    
    # Check environment variables
    required_vars = [
        "SIGNALS_BOT_TOKEN",
        "COPY_BOT_TOKEN", 
        "FUNDED_BOT_TOKEN",
        "POSTGRES_HOST",
        "POSTGRES_DB",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"❌ Missing environment variables: {missing_vars}")
        sys.exit(1)
    
    logger.info("✅ Environment variables validated")
    logger.info("🌟 Profitability Intelligence - Professional Trading Bot System")
    logger.info("📡 Signals Bot: @ProfitFeedNewsBot")
    logger.info("🔄 Copy Bot: @S2TCopyBot") 
    logger.info("💰 Funded Bot: @FundedS2TBot")
    logger.info("🌐 Admin API: Starting...")
    
    # Start all services
    try:
        asyncio.run(start_all_services())
    except KeyboardInterrupt:
        logger.info("🛑 Shutdown requested by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
