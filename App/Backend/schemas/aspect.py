from pydantic import BaseModel, Field
from datetime import datetime


class AspectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)


class AspectUpdate(BaseModel):
    is_active: bool


class AspectResponse(BaseModel):
    aspect_id: int = Field(...)
    name: str = Field(...)
    created_at: datetime = Field(...)
    is_active: bool = Field(...)

    class Config:
        from_attributes = True