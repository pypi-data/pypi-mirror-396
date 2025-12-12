import json
from typing import Optional, Any, Dict, List

import redis


class RedisManager:
    """Redis 管理器 - 提供完整的 Redis 操作封装"""

    def __init__(
            self,
            host: str = "localhost",
            port: int = 6379,
            db: int = 0,
            password: Optional[str] = None,
            decode_responses: bool = True,
            max_connections: int = 50
    ):
        """初始化 Redis 连接池"""
        self.pool = redis.ConnectionPool(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=decode_responses,
            max_connections=max_connections
        )
        self.client = redis.Redis(connection_pool=self.pool)

    def ping(self) -> bool:
        """检查 Redis 连接"""
        try:
            return self.client.ping()
        except redis.ConnectionError:
            return False

    # ============ String 操作 ============

    def set(
            self,
            key: str,
            value: Any,
            ex: Optional[int] = None,
            px: Optional[int] = None,
            nx: bool = False,
            xx: bool = False
    ) -> bool:
        """
        设置键值
        :param key: 键名
        :param value: 值（自动序列化 dict/list）
        :param ex: 过期时间（秒）
        :param px: 过期时间（毫秒）
        :param nx: 仅当键不存在时设置
        :param xx: 仅当键存在时设置
        """
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        return self.client.set(key, value, ex=ex, px=px, nx=nx, xx=xx)

    def get(self, key: str, json_decode: bool = False) -> Optional[Any]:
        """
        获取键值
        :param key: 键名
        :param json_decode: 是否尝试 JSON 解码
        """
        value = self.client.get(key)
        if value and json_decode:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return value

    def mget(self, keys: List[str], json_decode: bool = False) -> List[Optional[Any]]:
        """批量获取"""
        values = self.client.mget(keys)
        if json_decode:
            result = []
            for v in values:
                if v:
                    try:
                        result.append(json.loads(v))
                    except json.JSONDecodeError:
                        result.append(v)
                else:
                    result.append(None)
            return result
        return values

    def incr(self, key: str, amount: int = 1) -> int:
        """递增"""
        return self.client.incr(key, amount)

    def decr(self, key: str, amount: int = 1) -> int:
        """递减"""
        return self.client.decr(key, amount)

    # ============ Hash 操作 ============

    def hset(self, name: str, key: str, value: Any) -> int:
        """设置 hash 字段"""
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        elif isinstance(value, bool):
            value = str(value).lower()
        elif value is None:
            value = ''
        else:
            value = str(value)
        return self.client.hset(name, key, value)

    def hget(self, name: str, key: str, json_decode: bool = False) -> Optional[Any]:
        """获取 hash 字段"""
        value = self.client.hget(name, key)
        if value and json_decode:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return value

    def hgetall(self, name: str, json_decode: bool = False) -> Dict:
        """获取所有 hash 字段"""
        data = self.client.hgetall(name)
        if json_decode:
            result = {}
            for k, v in data.items():
                try:
                    result[k] = json.loads(v)
                except json.JSONDecodeError:
                    result[k] = v
            return result
        return data

    def hmset(self, name: str, mapping: Dict) -> bool:
        """
        批量设置 hash
        所有值必须转换为 bytes、string、int 或 float
        """
        if not mapping:
            return 0
        processed = {}
        for k, v in mapping.items():
            if isinstance(v, (dict, list)):
                processed[k] = json.dumps(v, ensure_ascii=False)
            elif isinstance(v, bool):
                # 布尔值转换为字符串 'true' 或 'false'
                processed[k] = str(v).lower()
            elif v is None:
                processed[k] = ''
            else:
                processed[k] = str(v)
        # return self.client.hset(name, mapping=processed)
        # 使用 pipeline 批量执行（最稳定的方式）
        pipe = self.client.pipeline()
        for k, v in processed.items():
            pipe.hset(name, k, v)
        results = pipe.execute()
        return sum(results)

    def hdel(self, name: str, *keys) -> int:
        """删除 hash 字段"""
        return self.client.hdel(name, *keys)

    # ============ List 操作 ============

    def lpush(self, key: str, *values) -> int:
        """左侧插入列表"""
        return self.client.lpush(key, *values)

    def rpush(self, key: str, *values) -> int:
        """右侧插入列表"""
        return self.client.rpush(key, *values)

    def lpop(self, key: str) -> Optional[str]:
        """左侧弹出"""
        return self.client.lpop(key)

    def rpop(self, key: str) -> Optional[str]:
        """右侧弹出"""
        return self.client.rpop(key)

    def lrange(self, key: str, start: int = 0, end: int = -1) -> List:
        """获取列表范围"""
        return self.client.lrange(key, start, end)

    def llen(self, key: str) -> int:
        """获取列表长度"""
        return self.client.llen(key)

    # ============ Set 操作 ============

    def sadd(self, key: str, *members) -> int:
        """添加集合成员"""
        return self.client.sadd(key, *members)

    def smembers(self, key: str) -> set:
        """获取所有集合成员"""
        return self.client.smembers(key)

    def srem(self, key: str, *members) -> int:
        """删除集合成员"""
        return self.client.srem(key, *members)

    def sismember(self, key: str, member: str) -> bool:
        """检查是否为集合成员"""
        return self.client.sismember(key, member)

    # ============ Sorted Set 操作 ============

    def zadd(self, key: str, mapping: Dict[str, float]) -> int:
        """添加有序集合成员"""
        return self.client.zadd(key, mapping)

    def zrange(
            self,
            key: str,
            start: int = 0,
            end: int = -1,
            withscores: bool = False
    ) -> List:
        """获取有序集合范围"""
        return self.client.zrange(key, start, end, withscores=withscores)

    def zrem(self, key: str, *members) -> int:
        """删除有序集合成员"""
        return self.client.zrem(key, *members)

    # ============ Key 操作 ============

    def delete(self, *keys) -> int:
        """删除键"""
        return self.client.delete(*keys)

    def exists(self, *keys) -> int:
        """检查键是否存在"""
        return self.client.exists(*keys)

    def expire(self, key: str, seconds: int) -> bool:
        """设置过期时间"""
        return self.client.expire(key, seconds)

    def ttl(self, key: str) -> int:
        """获取剩余过期时间"""
        return self.client.ttl(key)

    def keys(self, pattern: str = "*") -> List[str]:
        """获取匹配的键"""
        return self.client.keys(pattern)

    def scan(self, cursor: int = 0, match: str = "*", count: int = 10):
        """扫描键（推荐用于生产环境）"""
        return self.client.scan(cursor, match=match, count=count)

    def type(self, key: str) -> str:
        """获取键类型"""
        return self.client.type(key)

    def rename(self, src: str, dst: str) -> bool:
        """重命名键"""
        return self.client.rename(src, dst)

    # ============ 高级功能 ============

    def get_info(self) -> Dict:
        """获取 Redis 服务器信息"""
        return self.client.info()

    def get_memory_stats(self) -> Dict:
        """获取内存统计"""
        return self.client.info("memory")

    def flushdb(self) -> bool:
        """清空当前数据库"""
        return self.client.flushdb()

    def flushall(self) -> bool:
        """清空所有数据库"""
        return self.client.flushall()

    def close(self):
        """关闭连接"""
        self.client.close()
        self.pool.disconnect()


def sample_usage():
    # ============ 使用示例 ============

    # 方式1: 直接使用 RedisManager
    manager = RedisManager(host="localhost", port=6379)

    # String 操作
    manager.set("user:1001", {"name": "Alice", "age": 28}, ex=3600)
    user = manager.get("user:1001", json_decode=True)
    print(f"User: {user}")

    # Hash 操作
    manager.hmset("config:app", {
        "theme": "dark",
        "language": "zh-CN",
        "notifications": True
    })
    config = manager.hgetall("config:app")
    print(f"Config: {config}")

    # List 操作
    manager.rpush("queue:tasks", "task1", "task2", "task3")
    tasks = manager.lrange("queue:tasks")
    print(f"Tasks: {tasks}")

    # 计数器
    manager.incr("counter:visits")
    visits = manager.get("counter:visits")
    print(f"Visits: {visits}")

    manager.close()


if __name__ == "__main__":
    sample_usage()
