from fastapi import FastAPI, HTTPException, Depends, Request, Response
from uuid import UUID
import time
import random
import logging
from sqlalchemy.orm import Session
from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest


from vespera.api.models import Target, Check
from vespera.api.schemas import TargetIn, TargetOut, CheckOut
from vespera.common.db import get_db
from vespera.common.config import get_settings
from vespera.common.logging import setup_logging


FAULT_EXEMPT = {"/healthz", "/readyz", "/metrics"}

REQUESTS = Counter(
    "http_requests_total",
    "HTTP requests handled by the API",
    ["method", "route", "status", "app_version"],
)
LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "route", "app_version"],
)

def inject_fault(request: Request) -> None:
    rate = get_settings().fault_error_rate
    if rate > 0 and request.url.path not in FAULT_EXEMPT and random.random() < rate:
        raise HTTPException(status_code=500, detail="injected fault")

setup_logging("api")

log = logging.getLogger(__name__)

app = FastAPI(title="Vespera", dependencies=[Depends(inject_fault)])

FAULT_EXEMPT = {"/healthz", "/readyz", "/metrics"}

REQUESTS = Counter(
    "http_requests_total",
    "HTTP requests handled by the API",
    ["method", "route", "status", "app_version"],
)
LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "route", "app_version"],
)

def inject_fault(request: Request) -> None:
    rate = get_settings().fault_error_rate
    if rate > 0 and request.url.path not in FAULT_EXEMPT and random.random() < rate:
        raise HTTPException(status_code=500, detail="injected fault")

setup_logging("api")

log = logging.getLogger(__name__)

app = FastAPI(title="Vespera", dependencies=[Depends(inject_fault)])

@app.get("/")
def root():
    return {"app": "vespera"}

@app.post("/targets", status_code=201)
def create_target(target: TargetIn, db: Session = Depends(get_db)) -> TargetOut:
    new_target = Target(name=target.name, url=str(target.url))
    db.add(new_target)
    db.commit()
    db.refresh(new_target)
    return new_target


@app.get("/targets")
def list_targets(db: Session = Depends(get_db)) -> list[TargetOut]:
    return db.scalars(select(Target)).all()


@app.get("/targets/{target_id}")
def get_target(target_id: UUID, db: Session = Depends(get_db)) -> TargetOut:
    target = db.get(Target, target_id)
    if target is None:
        raise HTTPException(status_code=404, detail="Target not found")
    return target


@app.delete("/targets/{target_id}", status_code=204)
def delete_target(target_id: UUID, db: Session = Depends(get_db)) -> None:
    target = db.get(Target, target_id)
    if target is None:
        raise HTTPException(status_code=404, detail="Target not found")
    db.delete(target)
    db.commit()


@app.get("/readyz")
def readyz(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        raise HTTPException(status_code=503, detail="database unavailable")
    return {"status": "ready"}


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/targets/{target_id}/checks")
def list_checks(target_id: UUID, limit: int = 20, db: Session = Depends(get_db)) -> list[CheckOut]:
    target = db.get(Target, target_id)
    if target is None:
        raise HTTPException(status_code=404, detail="Target not found")
    return db.scalars(select(Check).where(Check.target_id == target.id).order_by(Check.id.desc()).limit(limit)).all()

@app.get("/version")
def version():
    return {"version": get_settings().vespera_version}

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start = time.perf_counter()
    status = "500"
    try:
        response = await call_next(request)
        status = str(response.status_code)
        return response
    finally:
        elapsed = time.perf_counter() - start
        route = request.scope.get("route")
        route = route.path if route else "unmatched"
        version = get_settings().vespera_version
        REQUESTS.labels(request.method, route, status, version).inc()
        LATENCY.labels(request.method, route, version).observe(elapsed)
        if request.url.path not in FAULT_EXEMPT:
            log.info("request", extra={"method": request.method, "route": route, "status": status, "duration_ms" : round(elapsed * 1000, 1)})


@app.get("/metrics", include_in_schema=False)
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

