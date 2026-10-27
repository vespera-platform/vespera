import asyncio
import logging
from typing import Literal
from fastapi import FastAPI, Response, Request
from pydantic import BaseModel

from vespera.common.logging import setup_logging
app = FastAPI(title="target-sim")

setup_logging("target-sim")
log = logging.getLogger(__name__)

mode: str = "up"

class Chaos(BaseModel):
    mode: Literal["up", "down", "slow"]

@app.get("/")
async def root():
    if mode == "up":
        return Response(status_code=200)
    elif mode == "down":
        return Response(status_code=503)
    elif mode == "slow":
        await asyncio.sleep(10)
        return Response(status_code=200)


@app.post("/chaos")
async def chaos(body: Chaos):
    global mode
    mode = body.mode
    return {"mode": mode}


@app.post("/hook")
async def hook(request: Request):
    body = await request.json()
    log.info("hook %s", body)
    return {"received": True}