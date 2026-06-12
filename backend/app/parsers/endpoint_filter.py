from typing import Any
from urllib.parse import unquote


def build_endpoint_key(endpoint: dict[str, Any]) -> str:
    return f"{endpoint.get('method', '').upper()} {endpoint.get('path', '')}"


def filter_endpoints(
    endpoints: list[dict[str, Any]],
    *,
    path_filter: str | None = None,
    method_filter: str | None = None,
    keyword_filter: str | None = None,
    group_filter: str | None = None,
    hash_hint: str | None = None,
) -> list[dict[str, Any]]:
    result = endpoints
    if path_filter:
        normalized_path = path_filter.strip()
        result = [
            item
            for item in result
            if item.get("path") == normalized_path or normalized_path.lower() in str(item.get("path", "")).lower()
        ]
    if method_filter:
        method = method_filter.upper()
        result = [item for item in result if str(item.get("method", "")).upper() == method]
    if group_filter:
        value = group_filter.strip().lower()
        result = [item for item in result if value in str(item.get("group_name") or "").lower()]
    if keyword_filter:
        value = keyword_filter.strip().lower()
        result = [item for item in result if _endpoint_text(item).find(value) >= 0]
    if hash_hint and not (path_filter or keyword_filter):
        hint_matches = _filter_by_hash_hint(result, hash_hint)
        if hint_matches:
            result = hint_matches
    return result


def _filter_by_hash_hint(endpoints: list[dict[str, Any]], hash_hint: str) -> list[dict[str, Any]]:
    decoded = unquote(hash_hint).lower()
    tokens = [token for token in decoded.replace("#", "/").replace("_", "/").replace("-", "/").split("/") if token]
    if not tokens:
        return []

    scored: list[tuple[int, dict[str, Any]]] = []
    for endpoint in endpoints:
        text = _endpoint_text(endpoint)
        score = sum(1 for token in tokens if token in text)
        if endpoint.get("path") and str(endpoint["path"]).lower() in decoded:
            score += 5
        if score > 0:
            scored.append((score, endpoint))
    scored.sort(key=lambda item: item[0], reverse=True)
    if not scored:
        return []
    top_score = scored[0][0]
    return [endpoint for score, endpoint in scored if score == top_score or score >= 2]


def _endpoint_text(endpoint: dict[str, Any]) -> str:
    tags = endpoint.get("tags") or []
    if not isinstance(tags, list):
        tags = [str(tags)]
    fields = [
        endpoint.get("name"),
        endpoint.get("group_name"),
        endpoint.get("summary"),
        endpoint.get("description"),
        endpoint.get("operation_id"),
        endpoint.get("path"),
        " ".join(str(tag) for tag in tags),
    ]
    return " ".join(str(field or "") for field in fields).lower()
