import shlex
from typing import Any
from urllib.parse import parse_qs, urlparse


def parse_curl_text(curl_text: str) -> dict[str, Any]:
    tokens = shlex.split(curl_text.replace("\\\n", " "))
    if not tokens or tokens[0].lower() != "curl":
        raise ValueError("curl text must start with curl")

    method = "GET"
    headers: dict[str, str] = {}
    body: str | None = None
    url: str | None = None

    index = 1
    while index < len(tokens):
        token = tokens[index]
        if token in ("-X", "--request") and index + 1 < len(tokens):
            method = tokens[index + 1].upper()
            index += 2
            continue
        if token.startswith("-X") and len(token) > 2:
            method = token[2:].upper()
            index += 1
            continue
        if token in ("-H", "--header") and index + 1 < len(tokens):
            _add_header(headers, tokens[index + 1])
            index += 2
            continue
        if token in ("-d", "--data", "--data-raw", "--data-binary", "--data-urlencode") and index + 1 < len(tokens):
            body = tokens[index + 1]
            if method == "GET":
                method = "POST"
            index += 2
            continue
        if not token.startswith("-") and url is None:
            url = token
        index += 1

    if not url:
        raise ValueError("curl text must contain request url")

    parsed = urlparse(url)
    path = parsed.path or "/"
    query = {key: values[0] if len(values) == 1 else values for key, values in parse_qs(parsed.query).items()}
    auth_required = any(key.lower() in {"authorization", "cookie"} for key in headers)

    endpoint = {
        "name": f"{method} {path}",
        "group_name": "curl",
        "method": method,
        "path": path,
        "description": None,
        "headers": headers or None,
        "request_params": {
            "query": query,
            "path": {},
        },
        "request_body_schema": {
            "raw": body,
        } if body is not None else None,
        "response_schema": None,
        "example_request": {
            "method": method,
            "url": url,
            "path": path,
            "headers": headers,
            "query": query,
            "body": body,
        },
        "example_response": None,
        "auth_required": auth_required,
        "tags": ["curl"],
    }
    return {
        "version": "curl",
        "title": "curl import",
        "endpoint_count": 1,
        "endpoints": [endpoint],
    }


def _add_header(headers: dict[str, str], header_line: str) -> None:
    if ":" not in header_line:
        return
    key, value = header_line.split(":", 1)
    headers[key.strip()] = value.strip()
