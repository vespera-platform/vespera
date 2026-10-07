import asyncio
import logging
import httpx

import redis.asyncio as aioredis
from redis.exceptions import ResponseError

from vespera.common.config import get_settings

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

STREAM = "vespera:events"
GROUP = "notifier"
CONSUMER = "N1"
SEND_TIMEOUT_S = 5
RETRY_DELAYS_S = (1, 2, 4)

async def ensure_group(rds) -> None:
    try:
        await rds.xgroup_create(STREAM, GROUP, id="$", mkstream=True)
    except ResponseError as e:
        if "BUSYGROUP" not in str(e):
            raise

async def send_with_retry(client, url: str, fields: dict, delays=RETRY_DELAYS_S) -> bool:
    for delay in (0, *delays):
        await asyncio.sleep(delay)
        try:
            r = await client.post(url, json=fields)
            if r.is_success:
                return True
            log.warning("hook event=%s -> HTTP %s", fields["id"], r.status_code)
        except httpx.HTTPError as e:
            log.warning("hook event=%s -> HTTP %s", fields["id"], e)
    return False

def entries_of(resp) -> list:
    return [e for _stream, entries in resp for e in entries]


async def main() -> None:
    rds = aioredis.Redis.from_url(get_settings().redis_url, decode_responses=True, socket_timeout=10)
    await ensure_group(rds)
    log.info("group ready")

    async with httpx.AsyncClient(timeout=SEND_TIMEOUT_S) as client:
        while True:
            pending = entries_of(await rds.xreadgroup(GROUP, CONSUMER, {STREAM: "0"}, count=10))
            batch = pending or entries_of(await rds.xreadgroup(GROUP, CONSUMER, {STREAM: ">"}, count=10, block=5000))
            for entry_id, fields in batch:
                ok = await send_with_retry(client, get_settings().webhook_url, fields)
                if ok:
                    await rds.xack(STREAM, GROUP, entry_id)
                    log.info("sent %s event %s", entry_id, fields["id"])


if __name__ == "__main__":
    asyncio.run(main())