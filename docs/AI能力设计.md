# AI 能力设计

## 当前阶段统一口径

- 第10阶段：鉴权 + 基础断言（已完成）
- 第10.1阶段：DSL + AI断言融合（已完成）
- 第10.2阶段：执行引擎可观测（已完成/稳定）

说明：第10.2阶段当前以执行稳定性、错误兜底、请求/响应/断言结果留痕、日志与报告路径可查看为准；当前不提供独立追踪编号或单独查询接口。

## 当前状态

第 11 阶段起，AI 用例生成支持通过 OpenAI-compatible Chat Completions 接入真实大模型。未配置 AI_API_KEY 时，用例生成接口会返回明确配置错误。

AI 模块位置：

```text
backend/app/ai
```

当前 mock 用例生成实现：

```text
backend/app/ai/testcase_generator_agent.py
```

第 9 阶段新增 mock HTML 辅助解析提示：

```text
backend/app/parsers/html_ai_parser.py
```

## AI 用例生成

`TestcaseGeneratorAgent` 输入 `api_endpoint`，输出结构化测试用例 JSON。

当前生成用例类型：

- `normal`
- `exception`
- `boundary`
- `auth`

当前 AI 生成断言建议：

- `status_code`
- `business_code`
- `business_success`
- `json_path_equal`
- `json_path_not_null`
- `json_path_not_empty`
- `json_path_contains`

执行引擎额外支持 `response_time`。

第 10.1 阶段后，AI 用例生成会根据接口响应示例或响应 Schema 生成断言建议。第 10.1 阶段起，AI 断言建议统一输出 DSL 字符串列表，保存到 `variables.ai_assertion_dsl`。

AI 输出示例：

```json
{
  "assertions": ["$.code == 200", "$.data != null"]
}
```

AI 断言规则：

- AI 只生成建议断言。
- AI 断言以 DSL 字符串表达。
- AI 断言默认不进入用户断言列表。
- AI 断言不直接决定 pass/fail。
- AI 不再把断言直接写成最终裁决规则。
- AI 不允许生成写死 `business_code = 1`。

## 第 9 阶段 AI 辅助解析边界

- 有 OpenAPI/Swagger 结构化文档时，优先使用结构化解析。
- 对 `doc.html`、Swagger UI 页面，只自动发现真实 JSON 文档，不直接把 HTML 页面当成接口结构来源。
- AI 辅助解析当前为 mock，只给出提示和边界说明。
- AI 输出必须是结构化 JSON。
- AI 输出必须经过校验后才允许入库。
- 不允许 AI 凭空编造接口参数并直接保存。
- 保存前必须允许用户编辑确认。
- 保存后的接口资产优先用于 AI mock 测试用例生成。
- AI mock 用例生成会优先使用用户编辑后的 Body JSON、query/path/header/cookie 参数示例和响应示例。
- 如果用户未编辑，则使用系统基于 example / default / schema 生成的默认可执行 JSON。

## 数据落库

- AI 生成的测试用例保存到 `test_case`。
- AI 调用记录保存到 `ai_analysis_record`。
- AI 断言建议保存到 `test_case.variables.ai_assertion_dsl`。
- 第 9 阶段接口文档导入仍保存到 `api_document` 和 `api_endpoint`。
- 第 9 阶段 `$ref` 展开结果和示例 / Schema 数据复用 `api_endpoint` 现有 JSON 字段保存，不新增数据库表。

## 断言系统2.0中的 AI 边界

- AI 是建议。
- 用户是控制。
- 系统是裁决。
- 最终断言由 `backend/app/core/assertion_engine_v2.py` 融合生成。
- DSL 与内部结构转换由 `backend/app/core/assertion_dsl.py` 完成。
- 断言融合优先级：`user > swagger > ai`。

## 当前限制

- 已接入真实 AI 用例生成能力，依赖环境变量配置模型服务。
- 未实现真实大模型从 HTML 页面自动还原完整接口结构。
- 未实现 AI 失败分析。
- 未实现 AI 报告总结。
- 未实现复杂接口依赖推理。
- 未让 AI 直接生成自由 Python 代码。

## 后续 AI 能力

- 第 12 阶段：接口依赖关系与链路用例
- 第 13 阶段：报告和失败分析增强

## 第 11 阶段真实 AI 用例生成

第 11 阶段已接入真实 AI 大模型生成可执行测试用例，当前采用 OpenAI-compatible Chat Completions HTTP 接口。

实现位置：

```text
backend/app/ai/llm_client.py
backend/app/ai/prompt_builder.py
backend/app/ai/swagger_case_model.py
backend/app/ai/testcase_standardizer.py
backend/app/ai/testcase_generator_agent.py
```

配置项：

```text
AI_API_BASE_URL
AI_API_KEY
AI_MODEL_NAME
AI_REQUEST_TIMEOUT
```

AI 输出标准：

```json
{
  "test_cases": [
    {
      "type": "normal|error|boundary",
      "request": {},
      "assertions": [
        {"type": "status_code", "expected": 200},
        {"type": "dsl", "expression": "$.code == 200"}
      ]
    }
  ]
}
```

标准化结果：

- 生成 `normal`、`error`、`boundary` 三类测试用例。
- 请求数据保存到 `test_case.steps`。
- DSL 断言建议保存到 `test_case.variables.ai_assertion_dsl`。
- AI 调用记录保存到 `ai_analysis_record`。
- 未配置 `AI_API_KEY` 时，用例生成接口返回明确配置错误。

边界：

- AI 不生成自由 Python 代码。
- AI 不直接修改 execution_engine。
- AI 不做接口链路编排。
- AI 不做失败分析和报告总结。

## 断言执行容错边界

AI 仍然只提供 mock 建议，不直接决定测试通过或失败。当前执行引擎对 AI/Swagger/用户断言融合后的 `final_assertions` 增加容错：

- AI 建议断言默认禁用，仅作为 skipped 建议展示。
- AI 生成的 DSL 如果无法转换为内部断言结构，不允许导致 run 接口 500。
- 断言执行阶段出现 DSL、JSONPath 或响应解析错误时，系统记录为 failed 断言结果。
- AI 不允许写死 `business_code = 1`，也不允许直接生成自由 Python 代码。
## 第11阶段专项修复：真实 OpenAI 用例生成

当前 AI 用例生成链路使用 OpenAI Python SDK 调用真实模型，入口为 `backend/app/ai/clients/openai_client.py`。兼容导出文件 `backend/app/ai/llm_client.py` 仅保留历史 import 兼容，不再实现手写 `httpx` LLM 调用。

运行时规则：

- `POST /api/v1/endpoints/{endpoint_id}/testcases/generate` 根据 `endpoint_id` 读取 `api_endpoint`，构建结构化接口模型后调用 OpenAI。
- `AI_API_KEY` 缺失时返回配置错误，不生成 mock 测试用例，不写入 `test_case`。
- mock/fake LLM 仅用于单元测试，不作为生产运行 fallback。
- 不在日志、响应或文档中输出完整 API Key。

OpenAI 输出必须为结构化 JSON：

```json
{
  "test_cases": [
    {
      "name": "正常查询",
      "type": "normal",
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
```

校验规则：

- `test_cases` 必须是非空数组，且必须包含 `normal`、`error`、`boundary` 三类用例。
- 每条用例必须包含 `name`、`type`、`request`、`assertions`。
- `type` 只能是 `normal`、`error`、`boundary`。
- `request.headers`、`request.query`、`request.path`、`request.body` 必须是对象。
- `assertions` 必须是 DSL 字符串数组，不再接受对象结构或 `suggestions` 结构。
- 非 JSON 或结构不合法时返回明确错误，不保存半成品。

## 第11阶段多模型接入：OpenAI / Qwen

AI 用例生成已增加统一模型适配层：

```text
backend/app/ai/llm_factory.py
```

支持供应商：

- `openai`：使用 `backend/app/ai/clients/openai_client.py`
- `qwen`：使用 `backend/app/ai/clients/qwen_client.py`，通过 DashScope OpenAI-compatible mode 调用

配置切换：

```text
AI_PROVIDER=openai
AI_API_BASE_URL=https://api.openai.com/v1
AI_MODEL_NAME=gpt-4o-mini
```

```text
AI_PROVIDER=qwen
AI_API_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
AI_MODEL_NAME=qwen-max-latest
```

统一规则：

- 所有 AI 用例生成都通过 `LLMFactory` 获取客户端。
- 业务服务不直接判断供应商，不直接调用 OpenAI SDK。
- OpenAI 分支使用 `response_format={"type": "json_object"}`。
- Qwen 分支不传 `response_format`，由平台对模型返回内容执行 JSON 强校验。
- 不允许 mock fallback 或 silent fallback。
- 输出仍统一为 `test_cases` 数组，断言统一为 DSL 字符串数组。
