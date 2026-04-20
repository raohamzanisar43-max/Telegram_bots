#!/usr/bin/env python3
"""
Offline bot starter - simulates bot functionality without network
"""
import os
import asyncio
import sys
from dotenv import load_dotenv

# Add current directory to Python path
sys.path.insert(0, '.')

load_dotenv()

async def simulate_bot():
    """Simulate bot functionality without network"""
    print("=== Profitability Intelligence Bot - Offline Mode ===")
    print()
    print("Bot Configuration:")
    print(f"  Token: {os.getenv('SIGNALS_BOT_TOKEN', 'Not set')[:20]}...")
    print(f"  Database: {os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}")
    print(f"  User: {os.getenv('POSTGRES_USER')}")
    print()
    
    # Test database connection
    try:
        import asyncpg
        conn = await asyncpg.connect(
            host=os.getenv('POSTGRES_HOST', 'localhost'),
            port=int(os.getenv('POSTGRES_PORT', '5432')),
            database=os.getenv('POSTGRES_DB', 'postgres'),
            user=os.getenv('POSTGRES_USER', 'postgres'),
            password=os.getenv('POSTGRES_PASSWORD', 'admin123')
        )
        
        # Check tables
        tables = await conn.fetch("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' ORDER BY table_name
        """)
        
        print("Database Status: CONNECTED")
        print(f"Tables: {len(tables)} found")
        
        await conn.close()
        print()
        
    except Exception as e:
        print(f"Database Error: {e}")
        return
    
    print("Bot Commands (when network is available):")
    print("  /start      - Register user")
    print("  /subscribe  - Subscribe to reports")
    print("  /daily      - Get daily performance")
    print("  /setlot 0.1 - Set lot size")
    print("  /help       - Show all commands")
    print()
    
    print("To use your bot:")
    print("1. Connect to different network (WiFi/hotspot/VPN)")
    print("2. Run: python signals_bot/main.py")
    print("3. Send /start to @hamzaaautomaiton_bot")
    print()
    
    print("Bot is READY - waiting for network access!")

if __name__ == "__main__":
    asyncio.run(simulate_bot())
