import logging
import time
import asyncio

import redis.asyncio as aioredis
import httpx
from sqlalchemy import select, update, func
import uuid
from datetime import datetime, timezone

from vespera.checker.probe import probe, TIMEOUT_S
from vespera.common.db import SessionLocal
from vespera.api.models import Target, Check
from vespera.common.config import get_settings

log = logging.getLogger(__name__)


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)  #  usuwanie powielajacych sie logow
    interval = get_settings().check_interval
    while True:
        start = time.perf_counter()
        asyncio.run(tick())
        log.info("tick took %.1f s", time.perf_counter() - start)
        time.sleep(interval)


def state(r) -> str:
    return "UP" if r.ok else "DOWN"

async def tick() -> None:
    with SessionLocal() as session:
        targets = session.scalars(select(Target)).all()

    sem = asyncio.Semaphore(20)

    async def check_one(client, t):
        async with sem:
            r = await probe(client, t.url)
        log.info("check %s %s -> %s", t.name, t.url, r)
        return t, r


    async with httpx.AsyncClient(timeout=TIMEOUT_S) as client:
        results = await asyncio.gather(*(check_one(client, t) for t in targets))


    with SessionLocal() as session:
        for t, r in results:
            session.add(Check(
                target_id=t.id,
                ok=r.ok,
                status_code=r.status_code,
                latency_ms=r.latency_ms,
                error=r.error
            ))
            session.execute(
                update(Target).where(Target.id == t.id).values(status=state(r), last_checked_at=func.now())
            )
        session.commit()

    events = [make_event(t, state(r)) for t, r in results if t.status is not None and t.status != state(r)]

    rds = aioredis.Redis.from_url(get_settings().redis_url)
    for e in events:
        await rds.xadd("vespera:events", e)
    await rds.aclose()

def make_event(t, new: str) -> dict:
    return {
        "id": str(uuid.uuid4()),
        "type": "target.state_changed",
        "target_id": str(t.id),
        "url": t.url,
        "old": t.status,
        "new": new,
        "at": datetime.now(timezone.utc).isoformat(),
    }

if __name__ == '__main__':
    main()