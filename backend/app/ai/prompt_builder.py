import json
from typing import Any


SYSTEM_PROMPT = """你是一个测试用例生成器，必须输出严格 JSON 格式。
禁止输出 Markdown、解释文字、注释或 Python 代码。
请根据输入的 Swagger/OpenAPI 接口结构生成可执行接口测试用例。
输出必须完全符合以下结构：
{
  "test_cases": [
    {
      "type": "normal|error|boundary",
      "name": "string",
      "description": "string",
      "request": {
        "headers": {},
        "query": {},
        "path": {},
        "body": {}
      },
      "assertions": [
        "status_code == 200",
        "$.code == 200",
        "$.data != null"
      ]
    }
  ]
}
Rules:
- Generate at least one normal, one error, and one boundary case.
- request 必须包含 headers、query、path、body 四个对象，其中 path 表示 path 参数。
- assertions 必须是 DSL 字符串数组，不允许输出对象、suggestions 或自然语言说明。
- DSL must be concise, for example: $.code == 200, $.data != null, status_code == 200.
- Do not generate expected business_code = 1.
- Do not invent undocumented fields when Swagger/OpenAPI provides structured schema or examples.
- Prefer examples/default values from the endpoint model.
"""


def build_testcase_generation_prompt(endpoint_model: dict[str, Any]) -> str:
    return json.dumps(
        {
            "task": "generate_executable_api_test_cases",
            "endpoint": endpoint_model,
            "output_contract": {
                "test_cases": [
                    {
                        "type": "normal|error|boundary",
                        "name": "string",
                        "description": "string",
                        "request": {"headers": {}, "query": {}, "path": {}, "body": {}},
                        "assertions": ["status_code == 200", "$.code == 200"],
                    }
                ]
            },
        },
        ensure_ascii=False,
    )
