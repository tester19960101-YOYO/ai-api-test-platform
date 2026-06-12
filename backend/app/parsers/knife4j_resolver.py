from dataclasses import dataclass, field
from typing import Any
from urllib.parse import quote, unquote, urljoin, urlsplit

import requests

from app.parsers.document_url_detector import build_candidate_spec_urls, split_document_url
from app.parsers.online_document_fetcher import fetch_url


AUTH_WARNING = (
    "当前接口文档需要登录态，请确认 Cookie 是否正确、是否过期，"
    "请确认 Cookie 是否属于当前文档系统；也可以尝试直接输入真实 OpenAPI JSON 地址，例如 /v3/api-docs/{group}。"
)


@dataclass
class ResolvedDocument:
    raw_document: dict[str, Any] | None
    raw_content: str | None
    resolved_spec_url: str | None
    detected_type: str
    hash_hint: str | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def resolve_openapi_from_url(url: str, timeout: int = 10, cookie: str | None = None) -> ResolvedDocument:
    parts = split_document_url(url)
    warnings: list[str] = []
    errors: list[str] = []
    group_hint = _extract_group_hint(parts.hash_hint)

    for candidate in _build_candidates_with_group(parts.clean_url, group_hint):
        try:
            fetched = fetch_url(candidate, timeout=timeout, cookie=cookie)
        except requests.RequestException as exc:
            if _is_auth_error(exc):
                _append_once(warnings, AUTH_WARNING)
            errors.append(f"{candidate}: {exc}")
            continue

        if isinstance(fetched.json_data, dict) and _is_openapi_document(fetched.json_data):
            return ResolvedDocument(
                raw_document=fetched.json_data,
                raw_content=fetched.content,
                resolved_spec_url=fetched.url,
                detected_type="openapi_json_url",
                hash_hint=parts.hash_hint,
                warnings=warnings,
                errors=errors,
            )
        if isinstance(fetched.json_data, dict) and _looks_like_auth_json(fetched.json_data):
            _append_once(warnings, AUTH_WARNING)
            errors.append(f"{candidate}: 接口文档返回 401/403 登录态错误。")
            continue

        if isinstance(fetched.json_data, list):
            grouped = _resolve_swagger_resources(parts.clean_url, fetched.json_data, timeout, cookie)
            warnings.extend(grouped.warnings)
            errors.extend(grouped.errors)
            if grouped.raw_document:
                grouped.hash_hint = parts.hash_hint
                return grouped

    warnings.append("未发现可解析的 OpenAPI/Swagger JSON，请确认 URL 是否可访问或手动粘贴 JSON 内容。")
    return ResolvedDocument(
        raw_document=None,
        raw_content=None,
        resolved_spec_url=None,
        detected_type="online_url",
        hash_hint=parts.hash_hint,
        warnings=warnings,
        errors=errors,
    )


def _resolve_swagger_resources(source_url: str, groups: list[Any], timeout: int, cookie: str | None) -> ResolvedDocument:
    origin = _origin(source_url)
    warnings: list[str] = []
    errors: list[str] = []
    candidates: list[str] = []

    for group in groups:
        if not isinstance(group, dict):
            continue
        group_url = group.get("url")
        if isinstance(group_url, str) and group_url:
            candidates.append(urljoin(origin, group_url))
        name = group.get("name") or group.get("group")
        if isinstance(name, str) and name:
            encoded_name = quote(name, safe="")
            candidates.append(urljoin(origin, f"/v3/api-docs/{encoded_name}"))
            candidates.append(urljoin(origin, f"/v2/api-docs?group={encoded_name}"))

    for candidate in _dedupe(candidates):
        try:
            fetched = fetch_url(candidate, timeout=timeout, cookie=cookie)
        except requests.RequestException as exc:
            if _is_auth_error(exc):
                _append_once(warnings, AUTH_WARNING)
            errors.append(f"{candidate}: {exc}")
            continue
        if isinstance(fetched.json_data, dict) and _is_openapi_document(fetched.json_data):
            return ResolvedDocument(
                raw_document=fetched.json_data,
                raw_content=fetched.content,
                resolved_spec_url=fetched.url,
                detected_type="swagger_resources",
                warnings=warnings,
                errors=errors,
            )
        if isinstance(fetched.json_data, dict) and _looks_like_auth_json(fetched.json_data):
            _append_once(warnings, AUTH_WARNING)
            errors.append(f"{candidate}: 接口文档返回 401/403 登录态错误。")

    warnings.append("swagger-resources 可访问，但未能继续解析到可用的分组文档。")
    return ResolvedDocument(
        raw_document=None,
        raw_content=None,
        resolved_spec_url=None,
        detected_type="swagger_resources",
        warnings=warnings,
        errors=errors,
    )


def _is_openapi_document(document: dict[str, Any]) -> bool:
    return bool(document.get("openapi") or document.get("swagger"))


def _looks_like_auth_json(document: dict[str, Any]) -> bool:
    code = str(document.get("code") or document.get("status") or "")
    message = str(document.get("msg") or document.get("message") or document.get("error") or "")
    return code in {"401", "403"} or "未能读取到有效 token" in message or "unauthorized" in message.lower()


def _is_auth_error(exc: requests.RequestException) -> bool:
    response = getattr(exc, "response", None)
    return bool(response is not None and response.status_code in {401, 403})


def _extract_group_hint(hash_hint: str | None) -> str | None:
    if not hash_hint:
        return None
    decoded = unquote(hash_hint).strip("/")
    if not decoded:
        return None
    group = decoded.split("/", 1)[0].strip()
    return group or None


def _build_candidates_with_group(url: str, group_hint: str | None) -> list[str]:
    parsed = urlsplit(url)
    origin = f"{parsed.scheme}://{parsed.netloc}"
    candidates: list[str] = []
    if group_hint:
        encoded_group = quote(group_hint, safe="")
        candidates.extend(
            [
                urljoin(origin, f"/v3/api-docs/{encoded_group}"),
                urljoin(origin, f"/v2/api-docs?group={encoded_group}"),
            ]
        )
    candidates.extend(build_candidate_spec_urls(url))
    return _dedupe(candidates)


def _append_once(items: list[str], item: str) -> None:
    if item not in items:
        items.append(item)


def _origin(url: str) -> str:
    parsed = urlsplit(url)
    return f"{parsed.scheme}://{parsed.netloc}"


def _dedupe(items: list[str]) -> list[str]:
    result = []
    seen = set()
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        result.append(item)
    return result
