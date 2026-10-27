import logging
import sys

from pythonjsonlogger.json import JsonFormatter

from vespera.common.config import get_common_settings

UVICORN_LOGGERS = ("uvicorn", "uvicorn.error", "uvicorn.access")


def setup_logging(component: str) -> None:
    settings = get_common_settings()

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(JsonFormatter(
        fmt=["levelname", "name", "message"],
        rename_fields={"levelname" : "level", "name": "logger", "message": "msg"},
        static_fields={"version" : settings.vespera_version, "component" : component},
        timestamp="ts"
    ))

    logging.basicConfig(handlers=[handler], level=settings.log_level.upper(), force=True)

    for name in UVICORN_LOGGERS:
        uv_log = logging.getLogger(name)
        if not uv_log.handlers and uv_log.propagate is False:
            continue
        uv_log.handlers.clear()
        uv_log.propagate = True