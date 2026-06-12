from typing import Any

from app.parsers.openapi_parser import parse_openapi_document


def parse_swagger_document(document: dict[str, Any]) -> dict[str, Any]:
    return parse_openapi_document(document)
