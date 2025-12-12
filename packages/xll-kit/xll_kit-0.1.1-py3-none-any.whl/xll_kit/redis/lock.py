from contextlib import contextmanager, asynccontextmanager
from xll_kit.redis.base import RedisBase


class RedisLock(RedisBase):
    """同步 + 异步的 Redis 分布式锁"""

    # -----------------------------
    # Sync Lock
    # -----------------------------
    @contextmanager
    def lock(self, key: str, timeout: int = 10):
        lock_key = self._key(key)
        token = "1"

        acquired = self.client.set(lock_key, token, nx=True, ex=timeout)
        if not acquired:
            raise RuntimeError(f"Lock {lock_key} already held")

        try:
            yield
        finally:
            if self.client.get(lock_key) == token:
                self.client.delete(lock_key)

    # -----------------------------
    # Async Lock
    # -----------------------------
    @asynccontextmanager
    async def alock(self, key: str, timeout: int = 10):
        lock_key = self._key(key)
        token = "1"

        acquired = await self.aclient.set(lock_key, token, nx=True, ex=timeout)
        if not acquired:
            raise RuntimeError(f"Lock {lock_key} already held")

        try:
            yield
        finally:
            cur = await self.aclient.get(lock_key)
            if cur == token:
                await self.aclient.delete(lock_key)
