import asyncio
from typing import Literal
from fastapi import FastAPI, Response
from pydantic import BaseModel

app = FastAPI(title="target-sim")

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