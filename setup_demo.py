#!/usr/bin/env python3
import redis
import bcrypt
import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from chat.config import get_config

def setup_demo_data():
    config = get_config()
    r = config.redis_client
    
    # Clear all data
    print("Clearing Redis data...")
    r.flushall()
    
    # Create demo users
    demo_users = ["Pablo", "Joe", "Mary", "Alex"]
    demo_password = "password123"
    
    print("Creating demo users...")
    for username in demo_users:
        # Hash password
        hashed_password = bcrypt.hashpw(demo_password.encode("utf-8"), bcrypt.gensalt(10))
        
        # Get next user ID
        next_id = r.incr("total_users")
        
        # Create user key
        user_key = f"user:{next_id}"
        username_key = f"username:{username}"
        
        # Store user data
        r.hset(user_key, mapping={
            "id": next_id,
            "username": username,
            "password": hashed_password.decode('utf-8')
        })
        
        # Map username to user ID
        r.hset(username_key, "id", next_id)
        
        print(f"✓ Created user: {username} (ID: {next_id})")
    
    print(f"\n🎉 Demo setup complete!")
    print(f"📊 Total users: {r.get('total_users').decode('utf-8') if r.get('total_users') else '0'}")
    print(f"🔑 Demo password for all users: {demo_password}")

if __name__ == "__main__":
    setup_demo_data()