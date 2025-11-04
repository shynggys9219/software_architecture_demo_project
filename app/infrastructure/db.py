import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.settings import settings

class Database:
    def __init__(self):
        self._client = None
        self._db = None

    async def client(self):
        if self._client is None:
            delay = 0.5
            for _ in range(10):
                try:
                    self._client = AsyncIOMotorClient(settings.MONGO_URI, serverSelectionTimeoutMS=3000)
                    await self._client.admin.command("ping")
                    break
                except Exception:
                    await asyncio.sleep(delay)
                    delay = min(delay * 2, 5)
            if self._client is None:
                self._client = AsyncIOMotorClient(settings.MONGO_URI)
        return self._client

    async def db(self):
        if self._db is None:
            client = await self.client()
            self._db = client[settings.DB_NAME]
        return self._db
