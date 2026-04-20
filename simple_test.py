#!/usr/bin/env python3
"""
Simple test with hardcoded values
"""
import asyncio
import psycopg2
from telegram.ext import Application

async def test_database():
    """Test database connection with hardcoded values"""
    print("Testing database connection...")
    try:
        conn = psycopg2.connect(
            host='localhost',
            port='5432',
            database='postgres',
            user='postgres',
            password='admin123'
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"Database connected: {version[0]}")
        
        # Test if tables exist
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        print(f"Tables found: {[table[0] for table in tables]}")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

async def test_bot_token():
    """Test bot token validity"""
    print("Testing bot token...")
    token = '8649263884:AAFPqrFae-ZaXp6M79NPKC_LlAdbKKAS_bU'
    
    try:
        app = Application.builder().token(token).build()
        bot_info = await app.bot.get_me()
        print(f"Bot connected: @{bot_info.username} ({bot_info.first_name})")
        return True
    except Exception as e:
        print(f"Bot connection failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("=== Bot Setup Test ===\n")
    
    # Test database
    db_ok = await test_database()
    print()
    
    # Test bot token
    bot_ok = await test_bot_token()
    print()
    
    # Summary
    if db_ok and bot_ok:
        print("All tests passed! Your bot is ready to use.")
    else:
        print("Some tests failed.")

if __name__ == "__main__":
    asyncio.run(main())
