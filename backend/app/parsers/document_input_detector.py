import json
import re
from typing import Literal


DocumentInputType = Literal[
    "online_url",
    "single_api_doc_url",
    "openapi_json_url",
    "openapi_json_text",
    "curl_text",
    "api_path",
    "unknown",
]

HTTP_METHODS = {"GET", "POST", "PUT", "DELETE", "PATCH"}
URL_PATTERN = re.compile(r"^https?://", re.IGNORECASE)
METHOD_PATH_PATTERN = re.compile(r"^(GET|POST|PUT|DELETE|PATCH)\s+(/\S*)$", re.IGNORECASE)


def detect_document_input_type(input_content: str) -> DocumentInputType:
    content = input_content.strip()
    lower_content = content.lower()
    if not content:
        return "unknown"

    if lower_content.startswith("curl "):
        return "curl_text"

    try:
        document = json.loads(content)
    except json.JSONDecodeError:
        document = None
    if isinstance(document, dict) and (document.get("openapi") or document.get("swagger")):
        return "openapi_json_text"

    if URL_PATTERN.match(content):
        if "#" in content:
            return "single_api_doc_url"
        if _looks_like_openapi_json_url(lower_content):
            return "openapi_json_url"
        return "online_url"

    if METHOD_PATH_PATTERN.match(content):
        return "api_path"

    if content.startswith("/"):
        return "api_path"

    return "unknown"


def parse_method_path_hint(input_content: str) -> tuple[str | None, str | None]:
    content = input_content.strip()
    match = METHOD_PATH_PATTERN.match(content)
    if match:
        return match.group(1).upper(), match.group(2)
    if content.startswith("/"):
        return None, content
    return None, None


def _looks_like_openapi_json_url(lower_url: str) -> bool:
    return any(
        token in lower_url
        for token in (
            "/v3/api-docs",
            "/v2/api-docs",
            "/api-docs",
            "/openapi.json",
            "/swagger.json",
            "/swagger-resources",
        )
    )
