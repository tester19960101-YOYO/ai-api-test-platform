from typing import Any

from pydantic import BaseModel, Field


class AssertionParseRequest(BaseModel):
    dsl: str = Field(..., min_length=1)


class AssertionParseResponse(BaseModel):
    dsl: str
    assertion: dict[str, Any]


class AssertionToDslRequest(BaseModel):
    assertion: dict[str, Any] | list[Any]


class AssertionToDslResponse(BaseModel):
    dsl: str | list[str]
