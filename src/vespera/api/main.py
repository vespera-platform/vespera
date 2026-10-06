from fastapi import FastAPI, HTTPException, Depends
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError

from vespera.api.models import Target
from vespera.api.schemas import TargetIn, TargetOut
from vespera.common.db import get_db

app = FastAPI(title="Vespera")


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