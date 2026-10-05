from uuid import UUID
from pydantic import BaseModel, HttpUrl

class TargetIn(BaseModel):
    name: str
    url: HttpUrl

class TargetOut(TargetIn):
    id: UUID