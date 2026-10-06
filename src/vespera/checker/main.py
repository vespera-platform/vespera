import logging
import time
from vespera.checker.probe import probe
from sqlalchemy import select
from vespera.common.db import SessionLocal
from vespera.api.models import Target
from vespera.common.config import get_settings

log = logging.getLogger(__name__)


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    interval = get_settings().check_interval
    while True:
        tick()
        time.sleep(interval)


def tick() -> None:
    with SessionLocal() as session:
        targets = session.scalars(select(Target)).all()
    for t in targets:
        result = probe(t.url)
        log.info("check %s %s -> %s", t.name, t.url, result)


if __name__ == '__main__':
    main()