#!/usr/bin/env python3
"""
Simple test script to verify bot configuration and database connectivity
"""
import os
import asyncio
from dotenv import load_dotenv
import psycopg2
from telegram.ext import Application

# Load environment variables
load_dotenv()

async def test_database():
    """Test database connection"""
    print("Testing database connection...")
    try:
        conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST', 'localhost'),
            port=os.getenv('POSTGRES_PORT', '5432'),
            database=os.getenv('POSTGRES_DB', 'postgres'),
            user=os.getenv('POSTGRES_USER', 'postgres'),
            password=os.getenv('POSTGRES_PASSWORD', 'admin123')
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✓ Database connected: {version[0]}")
        
        # Test if tables exist
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        print(f"✓ Tables found: {[table[0] for table in tables]}")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False

async def test_bot_token():
    """Test bot token validity"""
    print("Testing bot token...")
    token = os.getenv('SIGNALS_BOT_TOKEN')
    if not token:
        print("✗ SIGNALS_BOT_TOKEN not found in .env")
        return False
    
    try:
        app = Application.builder().token(token).build()
        bot_info = await app.bot.get_me()
        print(f"✓ Bot connected: @{bot_info.username} ({bot_info.first_name})")
        return True
    except Exception as e:
        print(f"✗ Bot connection failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("=== Profitability Intelligence Bot Setup Test ===\n")
    
    # Test database
    db_ok = await test_database()
    print()
    
    # Test bot token
    bot_ok = await test_bot_token()
    print()
    
    # Summary
    if db_ok and bot_ok:
        print("🎉 All tests passed! Your bot is ready to use.")
        print("\nNext steps:")
        print("1. Start the signals bot: python signals_bot/main.py")
        print("2. Send /start to your bot @hamzaaautomaiton_bot")
        print("3. Configure other bot tokens in .env as needed")
    else:
        print("❌ Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    asyncio.run(main())
