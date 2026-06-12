# AI 能力设计

## 当前阶段说明

第一阶段只预留 AI 模块目录，不实现真实 AI 调用。

第四阶段已实现 AI mock 用例生成能力。当前实现是 mock，不接真实大模型，不调用 OpenAI、Qwen 或其他真实模型。

第五阶段已实现 Pytest + Requests 基础执行引擎，第六阶段已实现 Vue3 前端 MVP 页面，第七阶段已完成 MVP 联调验收，第八阶段已固化 MVP 基线为 `v0.1.0-mvp`。执行失败时当前仍暂不接真实 AI 失败分析。

AI 模块位置：

```text
backend/app/ai
```

当前 AI mock 实现位置：

```text
backend/app/ai/testcase_generator_agent.py
```

## 当前 mock AI 策略

- 使用 mock `TestcaseGeneratorAgent`。
- 输入为 `api_endpoint` 接口资产结构。
- 输出为结构化测试用例 JSON。
- AI 不直接生成自由 Python 代码。
- AI 只生成结构化 JSON。
- AI 输出需要经过 schema 校验后再入库。
- Pytest 代码由第五阶段执行引擎通过模板生成，不由 AI 直接自由生成。

## 当前生成用例类型

当前 mock AI 会生成以下四类用例：

- `normal`：正常场景
- `exception`：异常参数场景
- `boundary`：边界值场景
- `auth`：鉴权场景

## 当前断言规则

当前 mock AI 生成基础断言规则：

- `status_code`
- `json_path_equal`
- `json_path_not_null`
- `json_path_contains`

第五阶段执行引擎额外支持 `response_time` 断言。

## 当前 API

AI mock 用例生成：

```text
POST /api/v1/endpoints/{endpoint_id}/testcases/generate
```

说明：

- 根据指定接口资产生成 mock 测试用例。
- 生成结果保存到 `test_case`。
- mock AI 调用记录保存到 `ai_analysis_record`。

## 数据落库

AI 相关分析记录保存到：

```text
ai_analysis_record
```

AI 生成的测试用例保存到：

```text
test_case
```

## 当前限制

- 未接真实 AI。
- 未调用真实大模型。
- 未实现 AI 失败分析。
- 未实现 AI 报告总结。
- 未实现在线接口文档 URL 导入与 AI 辅助解析。
- 未让 AI 直接生成自由 Python 代码。

## 后续 AI 能力

- 接口解析增强
- 在线接口文档 URL 导入与 AI 辅助解析
- 真实 AI 用例生成
- 断言生成增强
- 失败分析
- 报告总结

后续接入真实 AI 时，仍必须遵守：

- AI 不直接生成自由 Python 代码。
- AI 只生成结构化 JSON。
- AI 输出需要校验后再入库。
