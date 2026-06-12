from typing import Any

from fastapi.encoders import jsonable_encoder


def success_response(data: Any = None, message: str = "success") -> dict[str, Any]:
    return {
        "code": 0,
        "message": message,
        "data": jsonable_encoder(data),
    }


def error_response(code: int = 500, message: str = "internal server error", data: Any = None) -> dict[str, Any]:
    return {
        "code": code,
        "message": message,
        "data": jsonable_encoder(data),
    }
