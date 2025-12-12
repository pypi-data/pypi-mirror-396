from xll_kit.redis.base import RedisBase


class RedisPubSub(RedisBase):

    # Sync publish/subscribe
    def publish(self, channel: str, message: str):
        return self.client.publish(self._key(channel), message)

    def subscribe(self, channel: str):
        pub = self.client.pubsub()
        pub.subscribe(self._key(channel))
        return pub

    # Async publish/subscribe
    async def apublish(self, channel: str, message: str):
        return await self.aclient.publish(self._key(channel), message)

    async def asubscribe(self, channel: str):
        pub = self.aclient.pubsub()
        await pub.subscribe(self._key(channel))
        return pub
