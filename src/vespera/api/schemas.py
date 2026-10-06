from uuid import UUID
from pydantic import BaseModel, HttpUrl, ConfigDict

class TargetIn(BaseModel):
    name: str
    url: HttpUrl

class TargetOut(TargetIn):
    model_config = ConfigDict(from_attributes=True)
    id: UUID