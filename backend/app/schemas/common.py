from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)


class StatusUpdate(BaseModel):
    status: str = Field(..., min_length=1, max_length=32)
