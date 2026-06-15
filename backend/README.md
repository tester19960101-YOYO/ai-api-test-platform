# Backend README

## 后端简介

这是 AI API Test Platform / AI 接口自动化测试平台的后端服务。当前已完成 MVP 后端闭环，并在第 9 阶段支持多形态接口输入导入与 AI 辅助解析，在第 10 阶段支持环境鉴权配置与业务断言增强，在第 10.1 阶段支持断言系统 2.0 融合引擎和 DSL 可视化断言系统。

## 技术栈

- FastAPI
- SQLAlchemy
- Alembic
- Pydantic
- MySQL 8.0
- Pytest + Requests
- Jinja2、PyYAML、jsonpath-ng、pytest-html

## 后端目录结构

```text
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
  requirements.txt
  alembic.ini
  .env.example
```

## 环境变量配置

参考 `.env.example`：

```text
APP_NAME="AI API Test Platform"
APP_VERSION="0.1.0"
API_V1_PREFIX="/api/v1"
ENVIRONMENT="local"
LOG_LEVEL="INFO"
CORS_ORIGINS="*"
DATABASE_URL="mysql+pymysql://ai_test:ai_test@127.0.0.1:3306/ai_api_test_platform"
```

## 依赖安装

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 启动方式

```bash
cd backend
uvicorn app.main:app --reload
```

## 健康检查接口

```text
GET /api/v1/health
```

## 已实现内容

- FastAPI 应用初始化
- CORS 配置
- MySQL 数据库连接配置
- SQLAlchemy session
- 统一响应格式
- 统一异常处理
- 基础日志配置
- 9 张核心表 SQLAlchemy models
- 项目、环境、接口资产、测试用例 CRUD
- Swagger/OpenAPI 与 curl 导入解析
- 第 9 阶段多形态接口输入预览与保存
- mock AI 用例生成
- Pytest + Requests 基础执行引擎
- 环境级 token / cookie / header 鉴权配置
- 执行请求头合并
- 业务断言兜底
- 执行结果保存脱敏请求数据、响应体、curl 和断言结果
- 断言系统 2.0：融合用户断言、Swagger/OpenAPI 基础断言和 mock AI 断言建议
- DSL 断言解析和 JSON 转 DSL

## 第 9 阶段新增接口

```text
POST /api/v1/projects/{project_id}/documents/preview-url
POST /api/v1/projects/{project_id}/documents/import-url
```

支持：

- 在线 OpenAPI/Swagger JSON URL
- Knife4j / Swagger UI 页面 URL 自动发现真实 JSON 文档
- 单接口文档页面 URL hash hint 筛选
- 接口路径、请求方法、分组、关键词筛选
- Swagger/OpenAPI JSON 内容
- curl 文本
- 仅预览、保存选中、保存全部

边界：

- AI 当前仍为 mock。
- AI 不直接生成自由 Python 代码。
- AI 不凭空编造接口参数并直接保存。
- 保存前允许用户编辑确认。

## 执行接口

```text
POST /api/v1/executions/run
```

第 10 阶段执行增强：

- 环境公共 headers、环境鉴权 headers、测试用例请求 headers 自动合并。
- 合并优先级：环境公共 headers < 环境鉴权 headers < 测试用例请求 headers。
- 支持 `business_code`、`business_success`、`json_path_not_empty`。
- 响应包含 `code` 或 `success` 时会自动补充默认业务断言。
- 非 JSON 响应保存原始文本和 JSON 解析错误提示。
- 报告和日志不输出完整 token / cookie。

第 10.1 阶段断言增强：

- 新增 `backend/app/core/assertion_engine_v2.py`。
- 统一断言结构，支持 `source`、`type`、`path`、`operator`、`expected`、`priority`、`enabled`。
- 融合优先级：用户断言 > Swagger/OpenAPI 断言 > AI 建议断言。
- `business_code` 不再写死为 1，支持 `success_codes` 和 `success_expression`。
- `$.data` 相关 JSONPath 仅在业务成功后执行。
- mock AI 仅生成带 `confidence` 的建议断言，默认不控制 pass/fail。

v0.10.2 DSL 增强：

- 新增 `backend/app/core/assertion_dsl.py`。
- 新增 `POST /api/v1/assertion/parse` 和 `POST /api/v1/assertion/to-dsl`。
- 兼容 `POST /api/assertion/parse` 和 `POST /api/assertion/to-dsl`。
- 用户断言优先使用 DSL 字符串数组保存。
- AI mock 输出 `assertions: string[]`，保存为 `variables.ai_assertion_dsl`。

生成路径：

- 测试工程：`storage/generated/project_{project_id}/execution_{task_id}/`
- 报告：`storage/reports/execution_{task_id}/report.html`
- 日志：`storage/logs/execution_{task_id}/pytest.log`

## 验证方式

```bash
cd backend
python -m compileall app
python -m pytest
uvicorn app.main:app --reload
curl http://127.0.0.1:8000/api/v1/health
```

## 后续后端开发计划

- 第 11 阶段：真实 AI 大模型接入
- 第 12 阶段：接口依赖关系与链路用例
- 第 13 阶段：报告和失败分析增强
- 第 14 阶段：CI/CD、定时任务与权限系统
