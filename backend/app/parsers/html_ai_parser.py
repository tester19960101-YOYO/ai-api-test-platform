from typing import Any


def mock_parse_html_document(*, url: str, hash_hint: str | None = None) -> dict[str, Any]:
    return {
        "endpoints": [],
        "warnings": [
            "当前 AI 辅助解析为 mock 能力，仅用于提示；不会根据 HTML 页面凭空生成接口参数。",
            f"页面地址: {url}",
            f"筛选提示: {hash_hint}" if hash_hint else "未提供页面 hash 筛选提示。",
        ],
    }
