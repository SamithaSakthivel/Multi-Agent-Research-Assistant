import os
import motor.motor_asyncio
import redis.asyncio as aioredis

# ─── MongoDB ──────────────────────────────────────────────────────────────────

_mongo_client = None
_db = None


async def connect_db():
    global _mongo_client, _db
    uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    _mongo_client = motor.motor_asyncio.AsyncIOMotorClient(uri)
    _db = _mongo_client[os.getenv("MONGO_DB", "research_agent")]
    print(f"[DB] MongoDB connected → {uri}")


async def disconnect_db():
    if _mongo_client:
        _mongo_client.close()
        print("[DB] MongoDB disconnected")


def get_db():
    """Call after connect_db() has run (i.e. inside a request handler)."""
    if _db is None:
        raise RuntimeError("Database not initialised — call connect_db() first.")
    return _db


# ─── Redis ────────────────────────────────────────────────────────────────────

_redis = None


async def get_redis():
    global _redis
    if _redis is None:
        url = os.getenv("REDIS_URL", "redis://localhost:6379")
        _redis = aioredis.from_url(url, decode_responses=True)
        print(f"[DB] Redis connected → {url}")
    return _redis
