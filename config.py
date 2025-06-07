from pydantic import BaseModel, Field
from typing import Optional

class Config(BaseModel):
    Kards_resource: Optional[str] = Field(default="./data/kards")
