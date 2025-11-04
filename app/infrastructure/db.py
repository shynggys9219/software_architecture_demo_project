# app/infrastructure/db.py
import asyncio
import logging
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ServerSelectionTimeoutError, ConfigurationError
from app.settings import settings

logger = logging.getLogger("db")

class Database:
    def __init__(self) -> None:
        self._client: Optional[AsyncIOMotorClient] = None
        self._db = None

    async def client(self) -> AsyncIOMotorClient:
        if self._client is not None:
            return self._client

        last_err: Optional[Exception] = None
        delay = 0.5
        for _ in range(6):
            try:
                client = AsyncIOMotorClient(
                    settings.MONGO_URI,
                    serverSelectionTimeoutMS=5000,
                )
                await client.admin.command("ping")
                self._client = client
                break
            except (ServerSelectionTimeoutError, ConfigurationError) as e:
                last_err = e
                logger.warning("Mongo not ready yet: %s", e)
            except Exception as e:
                last_err = e
                logger.exception("Mongo init error: %s", e)
            await asyncio.sleep(delay)
            delay = min(delay * 2, 5)

        if self._client is None:
            logger.error("Mongo connection failed after retries: %s", last_err)
            self._client = AsyncIOMotorClient(settings.MONGO_URI)

        return self._client

    async def db(self):
        if self._db is not None:
            return self._db

        client = await self.client()

        try:
            default_db = client.get_default_database()
        except Exception:
            default_db = None

        if default_db is not None:
            self._db = default_db
        else:
            if not settings.DB_NAME:
                raise RuntimeError("DB_NAME is not set and URI has no default database")
            self._db = client[settings.DB_NAME]

        return self._db
