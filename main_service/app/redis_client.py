import redis
import json
from app.config import COORDINATES_REDIS_URL


class RedisClient:
    def __init__(self):
        self.redis = None

    def connect(self, urlStr=COORDINATES_REDIS_URL):
        self.redis = redis.from_url(urlStr, decode_responses=True)

    def get(self, key: str):
        return self.redis.get(key)

    def set(self, key: str, value: dict, ex: int = None):
        self.redis.set(key, json.dumps(value), ex=ex)

    def close(self):
        self.redis.close()


# Глобальный экземпляр клиента redis
redis_client_coordinates = RedisClient()
redis_client_price = RedisClient()

