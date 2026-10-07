import asyncio
import logging

import redis.asyncio as aioredis
from redis.exceptions import ResponseError

from vespera.common.config import get_settings

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

STREAM = "vespera:events"
GROUP = "notifier"

async def ensure_group(rds) -> None:
    try:
        await rds.xgroup_create(STREAM, GROUP, id="$", mkstream=True)
    except ResponseError as e:
        if "BUSYGROUP" not in str(e):
            raise

async def main() -> None:
    rds = aioredis.Redis.from_url(get_settings().redis_url, decode_responses=True)
    await ensure_group(rds)
    log.info("group ready")
    await rds.aclose()

if __name__ == "__main__":
    asyncio.run(main())