# app/redis/cache.py
from typing import Any
from xll_kit.redis.base import RedisBase


class RedisCache(RedisBase):

    def cache_set(self, key: str, value: Any, ttl: int = 3600):
        return self.set_json(key, value, ex=ttl)

    def cache_get(self, key: str):
        return self.get_json(key)

    async def acache_set(self, key: str, value: Any, ttl: int = 3600):
        return await self.aset_json(key, value, ex=ttl)

    async def acache_get(self, key: str):
        return await self.aget_json(key)
