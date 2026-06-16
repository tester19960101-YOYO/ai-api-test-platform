# AI 能力设计

## 当前状态

当前 AI 仍为 mock，不接真实大模型，不调用 OpenAI、Qwen 或其他真实模型。

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

## mock AI 用例生成

`TestcaseGeneratorAgent` 输入 `api_endpoint`，输出结构化测试用例 JSON。

当前生成用例类型：

- `normal`
- `exception`
- `boundary`
- `auth`

当前 AI mock 生成断言建议：

- `status_code`
- `business_code`
- `business_success`
- `json_path_equal`
- `json_path_not_null`
- `json_path_not_empty`
- `json_path_contains`

执行引擎额外支持 `response_time`。

第 10.1 阶段后，mock AI 用例生成会根据接口响应示例或响应 Schema 生成断言建议。`v0.10.2` 起，AI 断言建议统一输出 DSL 字符串列表，保存到 `variables.ai_assertion_dsl`。

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
- mock AI 调用记录保存到 `ai_analysis_record`。
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

- 未接真实 AI。
- 未实现真实大模型接口解析。
- 未实现 AI 失败分析。
- 未实现 AI 报告总结。
- 未实现复杂接口依赖推理。
- 未让 AI 直接生成自由 Python 代码。

## 后续 AI 能力

- 第 11 阶段：真实 AI 大模型接入
- 第 12 阶段：接口依赖关系与链路用例
- 第 13 阶段：报告和失败分析增强

## 断言执行容错边界

AI 仍然只提供 mock 建议，不直接决定测试通过或失败。当前执行引擎对 AI/Swagger/用户断言融合后的 `final_assertions` 增加容错：

- AI 建议断言默认禁用，仅作为 skipped 建议展示。
- AI 生成的 DSL 如果无法转换为内部断言结构，不允许导致 run 接口 500。
- 断言执行阶段出现 DSL、JSONPath 或响应解析错误时，系统记录为 failed 断言结果。
- AI 不允许写死 `business_code = 1`，也不允许直接生成自由 Python 代码。
