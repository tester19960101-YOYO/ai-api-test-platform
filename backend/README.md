# Backend README

## 后端简介

这是 AI API Test Platform / AI 接口自动化测试平台的后端服务。当前已完成基础工程、健康检查接口、后端基础 CRUD、接口文档导入与解析、AI mock 用例生成，以及 Pytest + Requests 基础执行引擎。第八阶段已固化 MVP 基线为 `v0.1.0-mvp`，后端 API 本阶段未新增。

## 技术栈

- 前端：Vue3 + TypeScript + Vite + Element Plus
- 后端：FastAPI + SQLAlchemy + Alembic + Pydantic
- 数据库：MySQL 8.0
- 执行引擎：Pytest + Requests
- 辅助库：Jinja2、PyYAML、jsonpath-ng、pytest-html

## 后端目录结构

```text
backend/
  app/
    main.py
    core/
    db/
    models/
    schemas/
    api/
      v1/
        health_api.py
        project_api.py
        environment_api.py
        api_endpoint_api.py
        api_document_api.py
        test_case_api.py
        ai_generation_api.py
        execution_api.py
      router.py
    services/
    repositories/
    parsers/
    ai/
    generator/
      project_generator.py
      templates/
        pytest_project/
    runner/
      pytest_runner.py
    storage/
  migrations/
  tests/
  requirements.txt
  alembic.ini
  .env.example
  README.md
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
copy .env.example .env
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
- 9 张核心表对应 SQLAlchemy models
- 项目、环境、接口资产、测试用例 CRUD
- OpenAPI 和 curl 导入解析
- mock AI 用例生成
- Pytest + Requests 基础执行引擎

## 执行接口

```text
POST /api/v1/executions/run
```

请求体示例：

```json
{
  "project_id": 1,
  "environment_id": 1,
  "case_ids": [1],
  "timeout": 10
}
```

说明：

- 根据数据库中的环境和测试用例生成临时 Pytest 工程。
- 生成工程保存到 `storage/generated/project_{project_id}/execution_{task_id}/`。
- 报告保存到 `storage/reports/execution_{task_id}/report.html`。
- 日志保存到 `storage/logs/execution_{task_id}/pytest.log`。
- 执行任务写入 `execution_task`。
- 执行结果写入 `execution_result`。
- 报告元信息写入 `test_report`。

## 验证方式

```bash
cd backend
python -m compileall app
python -m pytest
uvicorn app.main:app --reload
curl http://127.0.0.1:8000/api/v1/health
```

## 当前限制

- 不接真实 AI。
- 不让 AI 生成自由 Python 代码。
- 不做复杂接口依赖编排。
- 不做复杂 token 自动刷新。
- 不做 httpx 异步执行。
- 不做并发压测。
- 不做复杂 Allure 报告。
- 不做 WebSocket 实时日志。
- 不做生产级复杂前端交互和可视化编排。

## 后续后端开发计划

后续后端可围绕前端联调继续增强错误提示、查询筛选、分页细节和报告展示接口，但不提前实现复杂权限、SSO、CI/CD 或真实 AI。
