import time

import redis.asyncio as redis

from . import config

redis_client = redis.Redis(
    host=config.REDIS_HOST,
    port=config.REDIS_PORT,
    decode_responses=True,
)


async def fixed_window_check(client_id: str, limit: int, window_seconds: int):
    """
    Fixed-window rate limiting.

    Time is chopped into fixed buckets (e.g. 0-10s, 10-20s, ...). Each client
    gets one counter per bucket. Every request increments it; once it passes
    `limit`, further requests in that bucket are rejected.

    Returns (allowed, remaining, retry_after_seconds).
    """
    now = time.time()
    window_id = int(now // window_seconds)
    key = f"rl:fixed:{client_id}:{window_id}"

    count = await redis_client.incr(key)
    if count == 1:
        # First request in this window: make the key clean itself up
        await redis_client.expire(key, window_seconds)

    allowed = count <= limit
    remaining = max(0, limit - count)
    retry_after = window_seconds - int(now % window_seconds)
    return allowed, remaining, retry_after