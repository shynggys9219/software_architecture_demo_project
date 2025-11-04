# app/infrastructure/db.py
import asyncio, logging
import certifi
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

        ca = certifi.where()  # trust store
        delay = 0.5
        last_err: Optional[Exception] = None
        for _ in range(6):
            try:
                c = AsyncIOMotorClient(
                    settings.MONGO_URI,
                    serverSelectionTimeoutMS=5000,
                    tlsCAFile=ca,
                )
                await c.admin.command("ping")  # surface TLS/DNS issues early
                self._client = c
                break
            except (ServerSelectionTimeoutError, ConfigurationError) as e:
                last_err = e
                logger.warning("Mongo not ready: %s", e)
            except Exception as e:
                last_err = e
                logger.exception("Mongo init error: %s", e)
            await asyncio.sleep(delay)
            delay = min(delay * 2, 5)

        if self._client is None:
            logger.error("Mongo connection failed after retries: %s", last_err)
            # last fallback (still with CA so errors are clear)
            self._client = AsyncIOMotorClient(settings.MONGO_URI, tlsCAFile=ca)

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
            return self._db

        # Guard: DB not in URI, so we must have DB_NAME
        if not getattr(settings, "DB_NAME", None):
            raise RuntimeError(
                "Mongo DB name is not set: add it to the URI "
                "(.../yourdb?...) or set DB_NAME environment variable."
            )

        self._db = client[settings.DB_NAME]
        return self._db

