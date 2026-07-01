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

第 10.1 阶段后，AI 用例生成会根据接口响应示例或响应 Schema 生成断言建议。当前 AI 断言建议统一输出 DSL 字符串列表，保存到 `test_case.dsl_assertions`，并同步生成内部结构化 `test_case.assertions`。

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
- AI 断言建议保存到 `test_case.dsl_assertions`，结构化断言保存到 `test_case.assertions`。
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

AI 输出标准（当前权威结构）：

```json
{
  "test_strategy": {
    "normal": [],
    "error": [],
    "boundary": [],
    "security": []
  }
}
```

标准化结果：

- 生成 `normal`、`error`、`boundary`、`security` 四类测试用例。
- 请求数据保存到 `test_case.request_data`，接口信息冗余保存到 `endpoint_name` / `endpoint_path`。
- DSL 断言建议保存到 `test_case.dsl_assertions`，结构化断言保存到 `test_case.assertions`。
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

OpenAI / Qwen 输出必须为结构化 JSON：

```json
{
  "test_strategy": {
    "normal": [
      {
        "name": "正常查询",
        "purpose": "验证正常用户可以查询成功",
        "request": {"headers": {}, "query": {}, "path": {}, "body": {}},
        "assertions": ["status_code == 200", "$.code == 200", "$.data != null"],
        "risk_level": "P1",
        "reason": "覆盖主业务成功路径"
      }
    ],
    "error": [],
    "boundary": [],
    "security": []
  }
}
```

校验规则：

- 当前主输出结构为 `test_strategy`，并必须包含 `normal`、`error`、`boundary`、`security` 四类非空策略用例。
- 每条用例必须包含 `name`、`purpose`、`request`、`assertions`、`risk_level`、`reason`。
- `risk_level` 只能是 `P0`、`P1`、`P2`。
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
- 输出统一为 `test_strategy` 测试策略对象，断言统一为 DSL 字符串数组。

## 第11阶段 AI 测试策略生成增强

当前 AI 用例生成不再以“随机生成参数数据”为目标，而是要求模型按资深接口测试工程师思路输出可执行测试策略。

权威输出结构：

```json
{
  "test_strategy": {
    "normal": [],
    "error": [],
    "boundary": [],
    "security": []
  }
}
```

单条用例字段：

- `name`：用例名称。
- `purpose`：测试目的。
- `request`：请求结构，必须包含 `headers`、`query`、`path`、`body`。
- `assertions`：DSL 字符串数组。
- `risk_level`：`P0`、`P1`、`P2`。
- `reason`：设计原因。

测试设计维度：

- 功能正确性。
- 参数校验。
- 边界值分析。
- 异常路径覆盖。
- 安全风险，例如越权和注入。
- 业务语义验证。
- 数据依赖关系。

后端处理规则：

- `backend/app/ai/prompt_builder.py` 负责约束模型输出 `test_strategy`。
- `backend/app/ai/testcase_standardizer.py` 负责校验并标准化为现有 `test_case` 结构。
- 标准化结果保存为 `TestCaseUnifiedModel v1`：请求进入 `test_case.request_data`，DSL 进入 `test_case.dsl_assertions`，结构化断言进入 `test_case.assertions`，覆盖信息进入 `coverage_tag` / `ai_metadata`。
- 旧 `test_cases` 数组仅作为历史兼容入口，不再作为第11阶段主提示词规范。
- mock/fake LLM 仍只能用于单元测试，不作为运行时 fallback。

## Test Coverage Engine 1.0

第11阶段新增测试覆盖率引擎，位置：

```text
backend/app/services/coverage_engine.py
```

核心职责：

- 接收接口结构化模型。
- 生成 `coverage_matrix`。
- 生成每个测试维度的 `coverage_targets`。
- 将覆盖率计划传入 AI Prompt。
- 在标准化阶段校验 AI 输出是否覆盖完整维度。

固定覆盖维度：

- `functional`：功能正确性。
- `validation`：参数校验。
- `boundary`：边界值分析。
- `negative`：异常路径覆盖。
- `security`：安全测试，例如注入和越权。
- `business`：业务语义验证。
- `dependency`：数据依赖覆盖。

最小生成规则：

- `functional`：至少 1 条。
- `validation`：至少 2 条。
- `boundary`：至少 2 条。
- `negative`：至少 2 条。
- `security`：至少 1 条。
- `business`：至少 1 条。
- `dependency`：至少 1 条。

AI 输出的每条用例建议包含 `coverage_dimension`。如果任何维度缺失或低于最小数量，后端 Coverage Engine 会自动补齐缺失维度和最小数量，再统一标准化为测试用例；非 JSON、对象断言、空断言等结构性错误仍会返回明确失败，并且不保存半成品测试用例。
## AI 用例生成稳定性修复说明

当前 AI 用例生成接口使用真实大模型时，模型可能返回无法被平台 DSL 解析器识别的自然语言断言。后端标准化器会执行以下处理：

- `assertions` 仍要求为 DSL 字符串数组，不接受对象断言或 `suggestions` 结构。
- 对数组中的每条 DSL 字符串执行解析校验。
- 无法解析的 DSL 字符串会被丢弃，不再让 `ValueError` 冒泡为接口 500。
- 如果某条用例的所有 DSL 字符串都不可用，则根据该用例的 `coverage_dimension` 补入默认断言，例如功能类用例补入 `status_code == 200` 和 `$.data != null`。
- `business_code == 1` 仍禁止入库，不会被兜底为合法断言。

Test Coverage Engine 1.0 当前采用“模型生成 + 后端补齐”的策略：模型负责输出有业务语义的测试策略，后端负责补齐缺失或低于目标数量的覆盖维度，并在接口响应中返回 `coverage_matrix` 和 `coverage_summary` 供前端展示。

## TestCaseUnifiedModel v1

第 11 阶段后，AI 生成结果统一落地为 `TestCaseUnifiedModel v1`，不再以 `steps` / `variables` 作为主数据结构。

当前 AI 标准化规则：

- `coverage_dimension` 映射到 `type`，取值为 `functional`、`validation`、`boundary`、`negative`、`security`、`business`、`dependency`。
- `risk_level` 中的 `P0`、`P1`、`P2` 映射到 `priority`，并同步生成 `risk_level` 的 `high`、`medium`、`low`。
- `request.headers`、`request.query`、`request.path`、`request.body` 统一保存到 `request_data`。
- AI 输出的 DSL 字符串保存到 `dsl_assertions`。
- DSL 会转换为内部结构化 `assertions`，供执行层使用。
- 测试目的、设计原因、模型供应商、模型名称和覆盖来源保存到 `ai_metadata`。
- 覆盖维度标签保存到 `coverage_tag`。

AI 输出仍必须是结构化 JSON；如果返回非 JSON、对象断言、空断言或非法 DSL，后端会返回明确错误或执行默认断言补齐，不保存脏数据。

## AI 用例生成页面展示修复

当前 AI 用例生成接口返回的 `test_cases` 会先经过后端统一模型转换，再返回给前端：

- 历史 `steps` / `variables` 字段会兼容转换为 `request`、`dsl_assertions`、`coverage_tag`、`risk_level` 和 `ai_metadata`。
- 前端 AI 用例生成页按 `coverage_matrix` / `coverage_summary` 展示测试覆盖率卡片。
- 用例表格类型字段统一中文展示，不再直接展示 `normal`、`error`、`medium` 等旧英文枚举。
- 编辑抽屉从统一字段读取请求参数和 AI 断言建议；如果历史数据只有 `variables.ai_assertion_dsl`，后端会转换为 `dsl_assertions` 返回。
- 用户保存编辑后的断言 DSL 会同步写回 `test_case.dsl_assertions`，并生成内部结构化 `test_case.assertions`。
