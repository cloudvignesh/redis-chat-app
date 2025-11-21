import os
import redis
from werkzeug.utils import import_string


class ConfigMinimal(object):
    # Parse redis environment variables.
    redis_endpoint_url = os.environ.get("REDIS_ENDPOINT_URL", "127.0.0.1:6379")
    REDIS_HOST, REDIS_PORT = tuple(redis_endpoint_url.split(":"))
    REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", None)
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    
    redis_client = redis.Redis(
        host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, decode_responses=True
    )


def get_config() -> ConfigMinimal:
    return ConfigMinimal()