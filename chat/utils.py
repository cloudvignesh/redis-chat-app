import json
import math
import random
import bcrypt

from chat.config import get_config

SERVER_ID = random.uniform(0, 322321)

redis_client = get_config().redis_client


def make_username_key(username):
    return f"username:{username}"


def create_user(username, password):
    username_key = make_username_key(username)
    # Create a user
    hashed_password = bcrypt.hashpw(str(password).encode("utf-8"), bcrypt.gensalt(10))
    next_id = redis_client.incr("total_users")
    user_key = f"user:{next_id}"
    redis_client.hset(username_key, "id", next_id)
    redis_client.hset(user_key, "username", username)
    redis_client.hset(user_key, "password", hashed_password)
    redis_client.hset(user_key, "id", next_id)

    redis_client.sadd(f"user:{next_id}:rooms", "0")

    return {"id": next_id, "username": username}


def init_redis():
    """Initialize Redis connection"""
    try:
        redis_client.ping()
        print("Redis connection successful")
        return True
    except Exception as e:
        print(f"Redis connection failed: {e}")
        return False