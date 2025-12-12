# redisx/manager.py
from __future__ import annotations
import redis
import redis.asyncio as aioredis
from typing import Optional, Dict


class RedisManager:
    """通用 Redis 管理器，可作为独立库使用"""

    def __init__(self):
        # { "default": Redis, "cache": Redis, ...}
        self._sync_clients: Dict[str, redis.Redis] = {}
        self._async_clients: Dict[str, aioredis.Redis] = {}

    # -----------------------------
    # Sync Client
    # -----------------------------
    def get_client(
        self,
        name: str = "default",
        url: Optional[str] = None,
        *,
        max_connections: int = 20,
        decode_responses: bool = True,
    ) -> redis.Redis:

        """获取同步 Redis 客户端，不依赖任何 app 配置"""

        if name not in self._sync_clients:
            if not url:
                raise ValueError(f"Redis instance '{name}' not initialized and no URL provided")

            self._sync_clients[name] = redis.Redis.from_url(
                url,
                max_connections=max_connections,
                decode_responses=decode_responses,
            )

        return self._sync_clients[name]

    # -----------------------------
    # Async Client
    # -----------------------------
    def get_async_client(
        self,
        name: str = "default",
        url: Optional[str] = None,
        *,
        max_connections: int = 20,
        decode_responses: bool = True,
    ) -> aioredis.Redis:

        if name not in self._async_clients:
            if not url:
                raise ValueError(f"Redis instance '{name}' not initialized and no URL provided")

            self._async_clients[name] = aioredis.from_url(
                url,
                max_connections=max_connections,
                decode_responses=decode_responses,
            )

        return self._async_clients[name]

    # -----------------------------
    # Close
    # -----------------------------
    def close(self):
        for cli in self._sync_clients.values():
            cli.close()

    async def aclose(self):
        for cli in self._async_clients.values():
            await cli.aclose()


# 单例（可作为库级实例）
redis_manager = RedisManager()
