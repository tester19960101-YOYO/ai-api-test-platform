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

当前生成断言：

- `status_code`
- `json_path_equal`
- `json_path_not_null`
- `json_path_contains`

执行引擎额外支持 `response_time`。

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
- 第 9 阶段接口文档导入仍保存到 `api_document` 和 `api_endpoint`。
- 第 9 阶段 `$ref` 展开结果和示例 / Schema 数据复用 `api_endpoint` 现有 JSON 字段保存，不新增数据库表。

## 当前限制

- 未接真实 AI。
- 未实现真实大模型接口解析。
- 未实现 AI 失败分析。
- 未实现 AI 报告总结。
- 未实现复杂接口依赖推理。
- 未让 AI 直接生成自由 Python 代码。

## 后续 AI 能力

- 第 10 阶段：真实 AI 大模型接入
- 第 11 阶段：接口依赖关系与链路用例
- 第 13 阶段：报告和失败分析增强
