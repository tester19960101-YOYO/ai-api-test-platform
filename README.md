# AI API Test Platform

## 当前阶段统一口径

- 第10阶段：鉴权 + 基础断言（已完成）
- 第10.1阶段：DSL + AI断言融合（已完成）
- 第10.2阶段：执行引擎可观测（已完成/稳定）

说明：第10.2阶段当前以执行稳定性、错误兜底、请求/响应/断言结果留痕、日志与报告路径可查看为准；当前不提供独立追踪编号或单独查询接口。

## 当前阶段

已完成第 1-10.2 阶段：

- 第 1 阶段：项目骨架、后端基础工程、数据库表、SQLAlchemy models、健康检查、基础文档。
- 第 2 阶段：项目、环境、接口资产、测试用例基础 CRUD。
- 第 3 阶段：Swagger/OpenAPI JSON、文件、URL 和 curl 导入解析。
- 第 4 阶段：AI 用例生成。
- 第 5 阶段：Pytest + Requests 基础执行引擎。
- 第 6 阶段：Vue3 前端业务页面。
- 第 7 阶段：主流程联调验收与缺陷修复。
- 第 8 阶段：历史基线固化与演示准备（已归档）。
- 第 9 阶段：多形态接口输入导入与 AI 辅助解析。
- 第 10 阶段：鉴权 + 基础断言（已完成）。
- 第 10.1 阶段：DSL + AI 断言融合（已完成）。

## 技术栈

- 前端：Vue3 + TypeScript + Vite + Element Plus
- 后端：FastAPI + SQLAlchemy + Alembic + Pydantic
- 数据库：MySQL 8.0
- 执行引擎：Pytest + Requests
- 辅助库：Jinja2、PyYAML、jsonpath-ng、pytest-html

## 项目目录结构

```text
ai-api-test-platform/
  frontend/
    src/api/
    src/components/
    src/layouts/
    src/router/
    src/stores/
    src/types/
    src/utils/
    src/views/
  backend/
    app/
      api/
      ai/
      core/
      db/
      generator/
      models/
      parsers/
      repositories/
      runner/
      schemas/
      services/
      storage/
    migrations/
    tests/
  storage/
    uploads/
    generated/
    reports/
    logs/
  database/init.sql
  docs/
  AGENTS.md
  README.md
```

## 已完成内容

- 9 张核心表：`project`、`environment`、`api_document`、`api_endpoint`、`test_case`、`execution_task`、`execution_result`、`test_report`、`ai_analysis_record`
- FastAPI 后端基础工程、统一响应、统一异常、基础日志、健康检查
- 项目、环境、接口资产、测试用例基础 CRUD
- Swagger/OpenAPI、curl 导入解析
- 在线接口文档 URL 导入、Knife4j / Swagger UI 页面真实 JSON 地址自动发现
- 接口导入页支持填写 Cookie，用于抓取需要登录态的 Knife4j / Swagger 文档
- 接口导入页采用四步向导：选择导入方式、解析与预览、选择与编辑、导入结果；每一步单独展示相关内容
- 单接口文档页面 URL 的 hash hint 提取与接口筛选
- 接口路径、请求方法、名称、分组、关键词筛选
- OpenAPI / Swagger 基础 `$ref` 展开，支持 `components.schemas`、对象、数组、required、example、default
- 参数 JSON、Body JSON、响应 JSON 尽量基于 example / default / schema 生成可编辑示例
- 接口导入第 3 步提供左侧接口列表和右侧接口详情区，支持参数 JSON、Body JSON、响应 JSON 的“展开示例 / 展开 Schema”切换和保存预览修改
- “仅预览不保存”“保存选中接口”“保存全部接口”
- 未找到已有接口资产时创建待完善接口草稿
- 真实 AI 用例生成，AI 输出仅为结构化 JSON，并标准化为可执行测试用例
- Pytest + Requests 执行引擎、pytest-html 报告、执行日志
- Vue3 前端业务页面和接口联调入口
- 执行报告页支持多选测试用例执行，并可展开单条结果查看请求参数 JSON、响应体 JSON 和 curl 命令，支持复制
- 环境配置支持 `auth_type`、`token`、`cookie`、公共 headers、`auth_config_json`、timeout 和 retry 配置
- 执行测试时自动合并环境公共 headers、环境鉴权 headers 和用例请求 headers
- 业务断言支持 `business_code`、`business_success`、`json_path_not_empty`，并对响应 JSON 中的 `code` / `success` 提供默认业务断言兜底
- 执行结果保存脱敏后的请求数据、响应体、curl 命令和断言结果，避免在报告中暴露完整 token / cookie
- 断言系统2.0支持统一断言结构、来源追踪、优先级融合、同 path 去重
- AI 断言仅作为建议，默认不参与 pass/fail；用户断言优先级最高
- Swagger/OpenAPI 断言作为基础层，参与 status code、required 字段和 schema 结构断言
- 断言 DSL 可视化系统，用户通过 `$.code == 200`、`$.data != null` 等 DSL 管理断言，不再手写 JSON 断言
- 新增 DSL 解析和 JSON 转 DSL 接口

## 暂未实现内容

- 已支持通过 OpenAI-compatible Chat Completions 接入真实大模型；未配置 AI_API_KEY 时用例生成接口会返回配置错误
- 未实现 AI 凭 HTML 页面自动还原完整接口结构
- 未实现复杂接口依赖编排
- 未实现复杂 token/cookie 自动刷新
- 未实现 Word/PDF 解析
- 未实现权限系统、SSO、多用户协作
- 未实现 CI/CD、定时任务
- 未实现 WebSocket 实时日志
- 未实现生产级部署方案

## 后端启动方式

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

## 前端启动方式

```bash
cd frontend
npm install
npm run dev
```

默认访问：

```text
http://127.0.0.1:5173/
```

## MySQL 配置

默认配置：

```text
HOST: 127.0.0.1
PORT: 3306
DATABASE: ai_api_test_platform
USER: ai_test
PASSWORD: ai_test
```

初始化数据库：

```bash
mysql -uroot -p123456 < D:\aiTest\ai-api-test-platform\database\init.sql
```

## 健康检查接口

```text
GET /api/v1/health
```

期望返回：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "status": "ok"
  }
}
```

## 第 9 阶段导入接口

```text
POST /api/v1/projects/{project_id}/documents/preview-url
POST /api/v1/projects/{project_id}/documents/import-url
```

支持输入：

- 在线 OpenAPI/Swagger JSON URL
- Knife4j / Swagger UI 的 `doc.html`、`swagger-ui.html`、`swagger-ui/index.html`
- 单接口文档页面 URL，例如 `doc.html#/yingji/xxx/add_13`
- 接口路径，例如 `POST /saw/rainfallmonitor/add`
- Swagger/OpenAPI JSON 内容
- curl 文本
- 可选 Cookie，例如 `JSESSIONID=xxxx; SESSION=yyyy; token=zzzz`

保存规则：

- 有结构化文档时优先使用 OpenAPI/Swagger 解析。
- Cookie 只用于本次预览或导入请求，默认不保存到数据库，也不会在接口响应中返回。
- 文档示例与 Schema 展开结果可能存在差异，用户可在预览页编辑确认后保存。
- 保存后的接口资产会继续用于真实 AI 测试用例生成。
- AI 只基于结构化接口资产生成测试用例，不直接生成自由 Python 代码。
- 保存前支持预览、筛选和编辑确认。
- 不会导入后自动生成测试用例。
- 不支持自动登录、验证码、SSO 或浏览器自动化登录；如果 Cookie 过期，需要用户重新复制 Cookie。

## 第 10 阶段鉴权与业务断言

环境配置仍使用环境管理接口保存，不新增 API 路径。新增配置约定保存在 `environment.variables`：

- `auth_type`：`none`、`bearer`、`token`、`cookie`、`custom`
- `token`：执行测试时写入 `Authorization` 或自定义 token header
- `cookie`：执行测试时写入 `Cookie`
- `auth_config_json`：可配置 `token_header`、`token_prefix`、`headers` 等扩展鉴权信息
- `timeout_seconds`：环境默认超时时间
- `retry_count`：环境默认重试次数

执行请求头合并优先级：

```text
环境公共 headers < 环境鉴权 headers < 测试用例请求 headers
```

当前不支持自动 token 刷新、登录页跳转、验证码、SSO 或浏览器自动化登录。

## 第 10.1 阶段断言系统2.0

断言统一结构：

```json
{
  "id": "string",
  "source": "swagger | ai | user",
  "type": "status_code | json_path | business_code",
  "path": "$.code",
  "operator": "== | != | exists | contains",
  "expected": 200,
  "priority": 1,
  "enabled": true
}
```

融合规则：

```text
user > swagger > ai
```

- 用户断言优先级最高。
- Swagger 断言作为基础层参与执行。
- AI 断言只作为建议层，默认 `enabled=false`，不直接决定 pass/fail。
- 同一路径断言去重时保留最高优先级。
- `business_code` 支持 `success_codes` 和 `success_expression`，不再写死 1。
- `$.data` 相关断言仅在业务成功后执行。

## 第 10.1 阶段 断言 DSL 可视化系统

DSL 是唯一用户断言语言，JSON 断言结构只在执行层内部使用。

支持 DSL：

```text
$.code == 200
$.data != null
status_code == 200
$.msg contains 成功
```

支持操作：

```text
==  !=  >  <  contains  exists  not null
```

新增接口：

```text
POST /api/v1/assertion/parse
POST /api/v1/assertion/to-dsl
```

兼容别名：

```text
POST /api/assertion/parse
POST /api/assertion/to-dsl
```

前端测试用例编辑页提供：

- DSL 断言列表
- 新增 / 删除 / 编辑 / 复制
- 模板一键插入
- AI 建议 DSL 一键插入
- Swagger 断言 DSL 一键插入

AI mock 输出已简化为：

```json
{
  "assertions": ["$.code == 200", "$.data != null"]
}
```

AI DSL 默认保存为建议，不直接控制测试结果。

## 验证方式

后端：

```bash
cd backend
pip install -r requirements.txt
python -m compileall app
python -m pytest
uvicorn app.main:app --reload
curl http://127.0.0.1:8000/api/v1/health
```

前端：

```bash
cd frontend
npm install
npm run build
npm run dev
```

## 演示流程

1. 启动 MySQL 8.0。
2. 执行 `database/init.sql` 初始化数据库。
3. 启动后端。
4. 启动前端并打开 `http://127.0.0.1:5173/`。
5. 创建项目。
6. 配置环境。
7. 在接口导入页输入 OpenAPI/Swagger URL、doc.html URL、JSON 内容、curl 文本或接口路径。
8. 按四步向导完成“选择导入方式 -> 解析与预览 -> 选择与编辑 -> 导入结果”。
9. 在第 3 步按条件筛选、勾选接口、编辑确认 JSON 后，保存选中接口或保存全部接口。
10. 查看接口资产。
11. 选择接口调用真实 AI 生成可执行测试用例。
12. 管理测试用例。
13. 在执行报告页多选测试用例并执行测试。
14. 展开单条执行结果，查看并复制请求参数 JSON、响应体 JSON 和 curl 命令。
15. 查看执行结果和 pytest-html 报告。

## 下一阶段建议

- 第 12 阶段：接口依赖关系与链路用例
- 第 13 阶段：报告和失败分析增强
- 第 14 阶段：CI/CD、定时任务与权限系统

## 第 11 阶段真实 AI 用例生成

当前已支持通过 OpenAI-compatible Chat Completions 接口调用真实大模型生成可执行测试用例。

配置项位于 `backend/.env`：

```text
AI_API_BASE_URL="https://api.openai.com/v1"
AI_API_KEY="your-api-key"
AI_MODEL_NAME="gpt-4o-mini"
AI_REQUEST_TIMEOUT=60
```

生成接口保持不变：

```text
POST /api/v1/endpoints/{endpoint_id}/testcases/generate
```

AI 输出必须是结构化 JSON，并会被标准化为 `TestCaseUnifiedModel v1`：

- `type`：`functional`、`validation`、`boundary`、`negative`、`security`、`business`、`dependency`
- `request`：可执行请求结构，包含 `headers`、`query`、`path_params`、`body`
- `assertions`：结构化断言，供执行层内部使用
- `dsl_assertions`：用户侧可编辑的 DSL 断言字符串数组
- `coverage_tag`、`risk_level`、`ai_metadata`：覆盖维度、风险和 AI 生成元数据

本阶段不让 AI 生成自由 Python 代码。未配置 `AI_API_KEY` 时，用例生成接口会返回配置错误。

## 执行引擎稳定性修复

当前 `POST /api/v1/executions/run` 已增加执行稳定性兜底：生成 Pytest 工程、调用 pytest、读取 `results.jsonl`、DSL/JSONPath 断言执行过程中出现的非系统级异常，会转换为 `failed` 执行结果并写入 `execution_result.error_message`、`assertion_result`、执行日志和报告元信息，不再直接冒泡为 HTTP 500。

当前行为：

- DSL 解析失败、JSONPath 为空或非法、响应不是 JSON、断言执行异常，均记录为断言失败。
- pytest 超时或结果文件单行 JSON 损坏，会记录为 failed 结果。
- `business_code` 不写死为 1，继续使用 `success_codes` 或 `success_expression`。
- JSON 断言结构只用于后端执行层内部；用户侧仍以 DSL 为主要断言语言。
## 第11阶段 OpenAI 真实模型接入专项修复

当前 `POST /api/v1/endpoints/{endpoint_id}/testcases/generate` 已切换为真实 OpenAI Python SDK 调用链路。生产/开发运行时不再因为 `AI_API_KEY` 缺失而静默 fallback 到 mock 用例。

后端配置位于 `backend/.env`：

```text
AI_API_KEY=sk-xxxx
AI_API_BASE_URL=https://api.openai.com/v1
AI_MODEL_NAME=gpt-4o-mini
AI_REQUEST_TIMEOUT=60
```

生成规则：

- `AI_API_KEY` 缺失时返回明确错误：`AI_API_KEY 未配置，无法调用真实 OpenAI`。
- mock/fake LLM 仅允许在单元测试中通过 monkeypatch 或显式测试替身使用，不作为运行时兜底。
- AI 输出必须是结构化 JSON，根节点必须包含 `test_strategy` 对象。
- `test_strategy` 可继续按 `normal`、`error`、`boundary`、`security` 外层策略分组返回，但每条用例必须带 `coverage_dimension`，后端最终统一映射为 `TestCaseUnifiedModel v1.type`。
- 每条用例必须包含 `name`、`purpose`、`request`、`assertions`、`risk_level`、`reason`。
- `risk_level` 仅允许 `P0`、`P1`、`P2`。
- `request` 必须包含 `headers`、`query`、`path`、`body` 四类对象。
- `assertions` 必须是 DSL 字符串数组，例如 `["status_code == 200", "$.code == 200"]`。
- 模型返回非 JSON 或结构不合法时不会保存半成品测试用例。
- 本阶段不修改 execution_engine，不改变 DSL 语法，不新增数据库结构。

## 第11阶段多模型接入：OpenAI / Qwen

AI 用例生成现在通过统一工厂层创建模型客户端：

```text
backend/app/ai/llm_factory.py
```

调用链路：

```text
testcases/generate
  -> TestcaseGeneratorAgent
  -> LLMFactory
  -> OpenAIClient 或 QwenClient
  -> 统一 JSON 校验
  -> test_case / ai_analysis_record
```

配置 OpenAI：

```text
AI_PROVIDER=openai
AI_API_BASE_URL=https://api.openai.com/v1
AI_API_KEY=sk-xxxx
AI_MODEL_NAME=gpt-4o-mini
```

配置 Qwen / DashScope：

```text
AI_PROVIDER=qwen
AI_API_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
AI_API_KEY=sk-xxxx
AI_MODEL_NAME=qwen-max-latest
```

约束：

- 业务层不直接调用 OpenAI SDK，也不判断模型供应商。
- Qwen compatible mode 不传 `response_format`，由后端做 JSON 强校验。
- 不允许 mock fallback，不允许静默降级。
- 两类模型输出都必须标准化为 `test_strategy` 测试策略结构和 DSL 字符串断言。

## 第11阶段 AI 测试策略生成增强

AI 生成目标从“随机补数据”调整为“企业级接口测试策略设计”。模型输出必须严格为：

```json
{
  "test_strategy": {
    "normal": [
      {
        "name": "正常查询",
        "purpose": "验证正常用户可以查询成功",
        "request": {"headers": {}, "query": {}, "path": {}, "body": {}},
        "assertions": ["status_code == 200", "$.code == 200"],
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

后端校验规则：

- 模型输出必须覆盖 Coverage Engine 要求的 7 类维度，缺失维度会由后端补齐。
- 单条用例必须包含测试目的、设计原因和风险等级。
- DSL 断言入库前必须通过 `backend/app/core/assertion_dsl.py` 校验。
- 不允许 `business_code == 1` 这类写死旧业务码。
- 校验通过后，后端会标准化为 `TestCaseUnifiedModel v1`，请求保存到 `test_case.request_data`，结构化断言保存到 `test_case.assertions`，DSL 保存到 `test_case.dsl_assertions`，覆盖信息保存到 `test_case.coverage_tag` / `test_case.ai_metadata`，可直接进入执行引擎。
- 旧 `test_cases` 数组仅作为后端兼容入口保留，不再作为第11阶段主提示词输出规范。

## Test Coverage Engine 1.0

第11阶段新增测试覆盖率引擎：

```text
backend/app/services/coverage_engine.py
```

AI 用例生成链路已升级为：

```text
API Schema
  -> Coverage Engine
  -> coverage_matrix / coverage_targets
  -> AI 按维度生成 test_strategy
  -> 后端校验覆盖维度
  -> 标准化 test_case
  -> Execution Engine
```

覆盖矩阵固定包含 7 个维度：

```json
{
  "coverage_matrix": {
    "functional": true,
    "validation": true,
    "boundary": true,
    "negative": true,
    "security": true,
    "business": true,
    "dependency": true
  }
}
```

覆盖规则：

- `functional`：1-2 条。
- `validation`：2-3 条。
- `boundary`：2 条。
- `negative`：2-3 条。
- `security`：1-2 条。
- `business`：1 条。
- `dependency`：1 条。
- 模型输出的每条用例必须包含 `coverage_dimension`。
- 任一维度缺失或低于最小数量时，后端 Coverage Engine 会自动补齐缺失维度和最小数量，再统一标准化为测试用例。
- `POST /api/v1/endpoints/{endpoint_id}/testcases/generate` 返回 `coverage_matrix` 和 `coverage_summary`，便于前端展示覆盖情况。
- 前端 AI 用例生成请求单独设置 120 秒超时，用于兼容真实大模型和 Coverage Engine 生成 10 条左右用例时的较长响应时间；其他普通接口仍使用全局 20 秒超时。

## AI 用例生成接口稳定性说明

本次修复后，`POST /api/v1/endpoints/{endpoint_id}/testcases/generate` 针对真实大模型响应做了两类稳定性处理：

- 前端 `AI 用例生成` 请求单独使用 120 秒超时，避免真实模型和覆盖率补齐流程超过全局 20 秒超时后在浏览器 Network 中显示 `canceled`。
- 后端标准化阶段会校验 AI 返回的 DSL 断言。如果模型返回无法解析的 DSL 字符串，会丢弃该条非法断言，并按当前 `coverage_dimension` 补入默认安全断言，避免异常冒泡为 500。

接口成功返回时会包含 `coverage_matrix` 和 `coverage_summary`。前端 AI 用例生成页会在用例表格上方展示“测试覆盖率”卡片；如果请求被取消或生成失败，则不会展示该卡片。

## TestCaseUnifiedModel v1

当前测试用例统一使用 `TestCaseUnifiedModel v1` 作为 AI 生成、手工编辑、执行引擎和报告展示之间的数据契约。

核心字段：

- `endpoint`：接口 ID、名称、方法和路径。
- `type`：`functional`、`validation`、`boundary`、`negative`、`security`、`business`、`dependency`。
- `priority`：`P0`、`P1`、`P2`。
- `status`：`generated`、`edited`、`disabled`、`passed`、`failed`。
- `request` / `request_data`：统一请求结构。
- `assertions`：内部结构化断言。
- `dsl_assertions`：前端展示和编辑的 DSL 断言。
- `coverage_tag`：覆盖维度标签。
- `risk_level`：`low`、`medium`、`high`。
- `data_dependency`：数据依赖说明。
- `ai_metadata`：AI 生成来源、模型、目的、原因和覆盖来源。

历史 `steps` / `variables` 字段仅用于旧数据迁移和兼容读取，不作为当前前端展示和新用例生成的主结构。

### 测试用例页面兼容修复

当前测试用例列表、AI 用例生成页、执行报告页均通过后端统一模型读取测试用例数据：

- `GET /api/v1/projects/{project_id}/test-cases` 和 `GET /api/v1/testcases?project_id={project_id}` 均可返回统一测试用例结构。
- 历史测试用例的 `steps` / `variables` 会在后端读取时转换为 `request`、`dsl_assertions`、`coverage_tag`、`ai_metadata` 等统一字段。
- 前端编辑抽屉会展示请求参数、用户断言 DSL、AI 断言建议和结构化断言预览。
- 断言 DSL 模板包含 `$.code == 200`、`$.msg=="操作成功"`、`$.data != null`、`status_code == 200`。
- 接口导入预览遇到 401/403 时会提示用户检查 Cookie，不会把登录态失败误判为平台接口 404。
