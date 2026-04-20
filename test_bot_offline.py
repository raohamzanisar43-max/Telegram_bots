#!/usr/bin/env python3
"""
Offline bot test - simulates bot functionality without network
"""
import os
import asyncio
import asyncpg
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_database_operations():
    """Test database operations that the bot would use"""
    print("Testing database operations...")
    
    try:
        # Connect to database
        conn = await asyncpg.connect(
            host=os.getenv('POSTGRES_HOST', 'localhost'),
            port=int(os.getenv('POSTGRES_PORT', '5432')),
            database=os.getenv('POSTGRES_DB', 'postgres'),
            user=os.getenv('POSTGRES_USER', 'postgres'),
            password=os.getenv('POSTGRES_PASSWORD', 'admin123')
        )
        
        print("✓ Database connected successfully")
        
        # Test creating a user (what happens when /start is sent)
        telegram_id = 123456789
        username = "test_user"
        first_name = "Test User"
        
        # Insert user
        await conn.execute("""
            INSERT INTO users (telegram_id, username, first_name, language)
            VALUES ($1, $2, $3, 'en')
            ON CONFLICT (telegram_id) DO NOTHING
        """, telegram_id, username, first_name)
        
        print("✓ User creation test passed")
        
        # Test subscription (what happens when /subscribe is sent)
        user_id = await conn.fetchval(
            "SELECT id FROM users WHERE telegram_id = $1", telegram_id
        )
        
        await conn.execute("""
            INSERT INTO subscriptions (user_id, bot, active)
            VALUES ($1, 'signals', TRUE)
            ON CONFLICT (user_id, bot) DO UPDATE SET active = TRUE
        """, user_id)
        
        print("✓ Subscription test passed")
        
        # Test signals table (for channel listener)
        await conn.execute("""
            INSERT INTO signals (direction, pair, entry, sl, tp1, status, raw_text)
            VALUES ('BUY', 'EURUSD', 1.0850, 1.0800, 1.0900, 'open', 'Test signal')
        """)
        
        print("✓ Signal creation test passed")
        
        # Test signal snapshot (for daily reports)
        await conn.execute("""
            INSERT INTO signal_snapshots (pips_closed, pips_floating, pips_week, pips_month, closed_count, open_count)
            VALUES (150.5, 25.0, 380.0, 1200.0, 8, 3)
            ON CONFLICT (snapshot_date) DO UPDATE SET
                pips_closed = EXCLUDED.pips_closed,
                pips_floating = EXCLUDED.pips_floating,
                pips_week = EXCLUDED.pips_week,
                pips_month = EXCLUDED.pips_month,
                closed_count = EXCLUDED.closed_count,
                open_count = EXCLUDED.open_count
        """)
        
        print("✓ Signal snapshot test passed")
        
        # Test user settings (for /setlot command)
        await conn.execute("""
            INSERT INTO user_signals_settings (user_id, lot_size)
            VALUES ($1, 0.10)
            ON CONFLICT (user_id) DO UPDATE SET lot_size = EXCLUDED.lot_size
        """, user_id)
        
        print("✓ User settings test passed")
        
        # Query and display results
        users = await conn.fetch("SELECT * FROM users LIMIT 5")
        print(f"✓ Found {len(users)} users in database")
        
        signals = await conn.fetch("SELECT * FROM signals LIMIT 5")
        print(f"✓ Found {len(signals)} signals in database")
        
        snapshots = await conn.fetch("SELECT * FROM signal_snapshots ORDER BY snapshot_date DESC LIMIT 3")
        print(f"✓ Found {len(snapshots)} snapshots in database")
        
        await conn.close()
        print("✓ All database operations completed successfully")
        return True
        
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False

async def main():
    """Run offline bot tests"""
    print("=== Offline Bot Functionality Test ===\n")
    
    success = await test_database_operations()
    
    if success:
        print("\n🎉 Bot functionality test passed!")
        print("\nYour bot is ready to use. When you have network access:")
        print("1. Run: python signals_bot/main.py")
        print("2. Send /start to @hamzaaautomaiton_bot")
        print("3. Try commands: /subscribe, /daily, /setlot 0.1, /help")
    else:
        print("\n❌ Some tests failed. Check database configuration.")

if __name__ == "__main__":
    asyncio.run(main())
