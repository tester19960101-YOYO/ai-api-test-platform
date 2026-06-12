from dataclasses import dataclass
from urllib.parse import ParseResult, urljoin, urlsplit, urlunsplit


DOC_UI_MARKERS = ("doc.html", "swagger-ui.html", "swagger-ui/index.html")
SPEC_MARKERS = (
    "/v3/api-docs",
    "/v2/api-docs",
    "/api-docs",
    "/openapi.json",
    "/swagger.json",
    "/swagger-resources",
)


@dataclass(frozen=True)
class UrlParts:
    clean_url: str
    hash_hint: str | None
    parsed: ParseResult


def split_document_url(url: str) -> UrlParts:
    parsed = urlsplit(url)
    clean = urlunsplit((parsed.scheme, parsed.netloc, parsed.path, parsed.query, ""))
    return UrlParts(clean_url=clean, hash_hint=parsed.fragment or None, parsed=parsed)


def is_doc_ui_url(url: str) -> bool:
    lower_url = url.lower()
    return any(marker in lower_url for marker in DOC_UI_MARKERS)


def is_spec_json_url(url: str) -> bool:
    lower_url = url.lower()
    return any(marker in lower_url for marker in SPEC_MARKERS)


def build_candidate_spec_urls(url: str) -> list[str]:
    parts = split_document_url(url)
    origin = f"{parts.parsed.scheme}://{parts.parsed.netloc}"
    candidates = [
        parts.clean_url,
        urljoin(origin, "/v3/api-docs"),
        urljoin(origin, "/v2/api-docs"),
        urljoin(origin, "/swagger-resources"),
        urljoin(origin, "/api-docs"),
        urljoin(origin, "/openapi.json"),
        urljoin(origin, "/swagger.json"),
    ]
    return _dedupe(candidates)


def _dedupe(items: list[str]) -> list[str]:
    result = []
    seen = set()
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        result.append(item)
    return result
