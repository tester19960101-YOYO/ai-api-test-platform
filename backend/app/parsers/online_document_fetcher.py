import json
from dataclasses import dataclass
from typing import Any

import requests


@dataclass(frozen=True)
class FetchResult:
    url: str
    content: str
    json_data: Any | None


def normalize_cookie(cookie: str | None) -> str | None:
    if not cookie:
        return None
    value = " ".join(cookie.strip().splitlines()).strip()
    if value.lower().startswith("cookie:"):
        value = value.split(":", 1)[1].strip()
    return value or None


def fetch_url(url: str, timeout: int = 10, cookie: str | None = None) -> FetchResult:
    headers = {"Accept": "application/json,text/html;q=0.9,*/*;q=0.8"}
    normalized_cookie = normalize_cookie(cookie)
    if normalized_cookie:
        headers["Cookie"] = normalized_cookie
    response = requests.get(
        url,
        timeout=timeout,
        headers=headers,
    )
    response.raise_for_status()
    content = response.content.decode("utf-8-sig")
    try:
        json_data = json.loads(content)
    except ValueError:
        json_data = None
    return FetchResult(url=url, content=content, json_data=json_data)
