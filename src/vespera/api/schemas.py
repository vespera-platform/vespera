from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, HttpUrl, ConfigDict



class TargetIn(BaseModel):
    name: str
    url: HttpUrl

class TargetOut(TargetIn):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    status: str | None
    last_checked_at: datetime | None

class CheckOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    checked_at: datetime
    ok: bool
    status_code: int | None
    latency_ms: int | None
    error: str | None
