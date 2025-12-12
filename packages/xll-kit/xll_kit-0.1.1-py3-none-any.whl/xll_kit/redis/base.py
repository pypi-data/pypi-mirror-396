# redisx/base.py
import json
from typing import Any, Optional
from xll_kit.redis.manager import redis_manager


class RedisBase:
    """所有 Redis 组件的基础能力（同步 + 异步）"""

    def __init__(
        self,
        prefix: str = "",
        instance: str = "default",
        url: Optional[str] = None,
    ):
        self.prefix = prefix.rstrip(":") + ":" if prefix else ""
        self.instance = instance
        self.url = url

    # -----------------------------
    # 获取 Sync / Async Client
    # -----------------------------
    @property
    def client(self):
        return redis_manager.get_client(self.instance, url=self.url)

    @property
    def aclient(self):
        return redis_manager.get_async_client(self.instance, url=self.url)

    def _key(self, key: str) -> str:
        return f"{self.prefix}{key}"

    # -----------------------------
    # JSON 封装 (sync)
    # -----------------------------
    def set_json(self, key: str, value: Any, ex: Optional[int] = None):
        return self.client.set(self._key(key), json.dumps(value), ex=ex)

    def get_json(self, key: str):
        v = self.client.get(self._key(key))
        return json.loads(v) if v else None

    # -----------------------------
    # JSON 封装 (async)
    # -----------------------------
    async def aset_json(self, key: str, value: Any, ex: Optional[int] = None):
        return await self.aclient.set(self._key(key), json.dumps(value), ex=ex)

    async def aget_json(self, key: str):
        v = await self.aclient.get(self._key(key))
        return json.loads(v) if v else None
