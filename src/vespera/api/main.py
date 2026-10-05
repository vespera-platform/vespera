from fastapi import FastAPI, HTTPException
from uuid import UUID, uuid4
from vespera.api.schemas import TargetIn, TargetOut


app = FastAPI(title="Vespera")

@app.get("/")
def root():
    return {"app": "vespera"}

TARGETS: dict[UUID, TargetOut] = {}

@app.post("/targets", status_code=201)
def create_target(target: TargetIn) -> TargetOut:
    new_target = TargetOut(id=uuid4(), **target.model_dump())
    TARGETS[new_target.id] = new_target
    return new_target

@app.get("/targets")
def list_targets() -> list[TargetOut]:
    return list(TARGETS.values())

@app.get("/targets/{target_id}")
def get_target(target_id: UUID) -> TargetOut:
    if target_id not in TARGETS:
        raise HTTPException(status_code=404, detail="Target not found")
    return TARGETS[target_id]

@app.delete("/targets/{target_id}", status_code=204)
def delete_target(target_id: UUID) -> None:
    if target_id not in TARGETS:
        raise HTTPException(status_code=404, detail="Target not found")
    del TARGETS[target_id]