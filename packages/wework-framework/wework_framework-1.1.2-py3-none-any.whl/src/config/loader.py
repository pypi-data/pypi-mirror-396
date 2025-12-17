import asyncio, os, json
from src.db.repos import ConfigRepo
from src.config.settings import settings
import redis.asyncio as aioredis


class ConfigLoader:
    def __init__(self):
        self._cfg = {
            # Generic configuration - add your own settings here
            # Example: 'app_name': settings.app_name,
        }
        self.repo = ConfigRepo()
        self._redis = None
        self._listener_task = None

    async def load(self):
        rows = await self.repo.list_configs()
        for r in rows:
            self._cfg[r['key']] = self._coerce_type(r['value'])
        return self._cfg

    async def persist(self, key, value):
        await self.repo.upsert_config(key, str(value))
        if self._redis is None:
            self._redis = await aioredis.from_url(settings.redis_url)
        await self._redis.publish('cfg_updates', json.dumps({'key': key, 'value': str(value)}))

    def get(self, key, default=None):
        return self._cfg.get(key, default)

    def set(self, key, value):
        self._cfg[key] = value
        asyncio.create_task(self.persist(key, value))

    async def start_listener(self):
        if self._redis is None:
            self._redis = await aioredis.from_url(settings.redis_url)
        pub = self._redis.pubsub()
        await pub.subscribe('cfg_updates')

        async def _loop():
            async for msg in pub.listen():
                if msg is None or msg.get('type') != 'message':
                    continue
                try:
                    parsed = json.loads(msg.get('data'))
                    k = parsed.get('key');
                    v = parsed.get('value')
                    self._cfg[k] = self._coerce_type(v)
                except Exception:
                    pass

        self._listener_task = asyncio.create_task(_loop())

    def _coerce_type(self, v: str):
        if v is None:
            return v
        for caster in (int, float):
            try:
                return caster(v)
            except Exception:
                pass
        if isinstance(v, str) and v.lower() in ('true', 'false'):
            return v.lower() == 'true'
        return v
