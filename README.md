# AI API Test Platform

## 项目简介

AI API Test Platform / AI 接口自动化测试平台，用于管理接口资产、导入和解析接口文档、使用 mock AI 生成结构化接口测试用例，并通过 Pytest + Requests 执行接口自动化测试，沉淀执行结果和测试报告。当前 MVP 主流程已跑通，已固化为 `v0.1.0-mvp`，适合演示和继续迭代。

## 当前阶段

当前已完成第一阶段到第八阶段，MVP 基线版本为 `v0.1.0-mvp`。

- 第一阶段：项目骨架、后端基础工程、数据库表设计、SQLAlchemy models、健康检查接口、基础配置和基础文档。
- 第二阶段：后端基础 CRUD，包括项目管理、环境管理、接口资产基础管理、测试用例基础管理。
- 第三阶段：接口文档导入与解析，包括 Swagger/OpenAPI JSON 内容导入、JSON 文件导入、URL 导入和 curl 文本导入。
- 第四阶段：AI mock 用例生成，包括 mock agent、结构化用例 JSON、输出校验、生成用例入库和 AI 分析记录入库。
- 第五阶段：Pytest + Requests 基础执行引擎，包括生成临时测试工程、调用 Pytest、保存执行任务、执行结果和测试报告。
- 第六阶段：Vue3 前端 MVP 页面，包括项目管理、环境配置、接口导入、接口列表、接口详情、AI mock 用例生成、测试用例管理、执行结果 / 测试报告页面。
- 第七阶段：MVP 联调验收与缺陷修复，已完成后端、前端、数据库、AI mock、Pytest + Requests 执行引擎和报告路径的完整主流程验收。
- 第八阶段：MVP 基线固化与演示准备，补充演示指南、已知问题、后续优化路线和版本记录，标记当前 MVP 为 `v0.1.0-mvp`。

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
    src/
      api/
      components/
      layouts/
      router/
      stores/
      types/
      utils/
      views/
    package.json
    vite.config.ts
    .env.example
  backend/
    app/
      main.py
      core/
      db/
      models/
      schemas/
      api/
      services/
      repositories/
      parsers/
      ai/
      generator/
        templates/
          pytest_project/
      runner/
      storage/
    migrations/
    tests/
    requirements.txt
    alembic.ini
    .env.example
    README.md
  storage/
    uploads/
    generated/
    reports/
    logs/
  database/
    init.sql
  docs/
  AGENTS.md
  README.md
```

## 已完成内容

- FastAPI 后端基础工程
- MySQL 初始化 SQL 和 9 张 MVP 核心表
- SQLAlchemy models
- Alembic 基础配置
- 统一响应格式、统一异常处理、基础日志配置
- `GET /api/v1/health`
- 项目、环境、接口资产、测试用例 CRUD
- Swagger/OpenAPI 和 curl 导入解析
- mock AI 用例生成
- Pytest + Requests 基础执行引擎
- pytest-html 报告生成
- 执行日志和执行报告元信息沉淀
- Vue3 + TypeScript + Vite 前端工程
- Element Plus、Vue Router、Pinia、Axios 基础集成
- 前端 MVP 页面和后端 API 基础联调入口
- MVP 主流程联调验收
- MVP 演示指南、已知问题说明和版本记录
- 基础自动化测试和前端构建验证
- 基础文档

## 当前 MVP 状态

- MVP 版本：`v0.1.0-mvp`
- MVP 主流程：已跑通
- 当前用途：可演示、可继续迭代
- AI 状态：当前仍为 mock AI，未接真实大模型
- 执行引擎：Pytest + Requests
- 报告方案：pytest-html
- 在线接口文档 URL 导入与 AI 辅助解析：未实现，规划放到第 9 阶段

## 暂未实现内容

- 未接真实 AI
- 未实现真实大模型调用
- 未让 AI 直接生成自由 Python 代码
- 未实现复杂接口依赖编排
- 未实现复杂 token 自动刷新
- 未实现权限系统
- 未实现 CI/CD
- 未实现 SSO 登录
- 未实现验证码或扫码登录
- 未实现 Word/PDF 解析
- 未实现 httpx 异步执行
- 未实现并发压测
- 未实现复杂 Allure 报告
- 未实现 WebSocket 实时日志
- 未实现生产级复杂前端交互和可视化编排

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

默认访问地址：

```text
http://127.0.0.1:5173/
```

前端默认通过 Vite proxy 将 `/api/v1` 转发到：

```text
http://127.0.0.1:8000
```

## MySQL 配置

默认连接配置：

```text
HOST: 127.0.0.1
PORT: 3306
DATABASE: ai_api_test_platform
USER: ai_test
PASSWORD: ai_test
```

对应 SQLAlchemy 连接字符串：

```text
mysql+pymysql://ai_test:ai_test@127.0.0.1:3306/ai_api_test_platform
```

## 数据库初始化方式

```bash
mysql -uroot -p123456 < D:\aiTest\ai-api-test-platform\database\init.sql
```

如果当前 PowerShell 不支持 `<` 重定向，可以使用：

```powershell
& "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -uroot -p123456 -e "source D:/aiTest/ai-api-test-platform/database/init.sql"
```

核心表固定为：

```text
project
environment
api_document
api_endpoint
test_case
execution_task
execution_result
test_report
ai_analysis_record
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

## API 概览

接口文档导入：

```text
POST /api/v1/projects/{project_id}/api-documents/openapi
POST /api/v1/projects/{project_id}/api-documents/openapi-file
POST /api/v1/projects/{project_id}/api-documents/curl
```

AI mock 用例生成：

```text
POST /api/v1/endpoints/{endpoint_id}/testcases/generate
```

Pytest + Requests 执行：

```text
POST /api/v1/executions/run
```

## 前端路由

```text
/projects
/environments
/api-import
/endpoints
/endpoints/:id
/ai-cases
/test-cases
/reports
```

## 执行引擎输出位置

生成工程目录：

```text
storage/generated/project_{project_id}/execution_{task_id}/
```

报告目录：

```text
storage/reports/execution_{task_id}/report.html
```

日志目录：

```text
storage/logs/execution_{task_id}/pytest.log
```

生成出来的测试工程不要放进 `backend/app`。

## 验证方式

后端验证：

```bash
cd backend
pip install -r requirements.txt
python -m compileall app
python -m pytest
uvicorn app.main:app --reload
curl http://127.0.0.1:8000/api/v1/health
```

前端验证：

```bash
cd frontend
npm install
npm run type-check
npm run build
npm run dev
```

## 完整演示流程

演示前准备：

1. 启动 MySQL 8.0。
2. 执行 `database/init.sql` 初始化数据库。
3. 启动后端服务。
4. 启动前端服务。
5. 打开 `http://127.0.0.1:5173/`。

页面演示路径：

1. 在项目管理页创建项目。
2. 进入项目工作区。
3. 在环境配置页创建环境，配置 `base_url`、headers、timeout 等信息。
4. 在接口导入页导入 Swagger/OpenAPI JSON 或 curl 文本。
5. 在接口列表页查看导入后的接口资产。
6. 在接口详情页查看接口结构。
7. 在 AI 用例生成页生成 mock AI 测试用例。
8. 在测试用例管理页查看、编辑或禁用测试用例。
9. 在执行报告页选择环境和测试用例，执行测试。
10. 查看执行结果、报告路径和日志路径。

## MVP 验收

第七阶段已完成 MVP 联调验收。验收报告位置：

```text
docs/MVP验收报告.md
```

验收结论：MVP 主流程已跑通，当前达到可演示、可继续迭代状态。

## 演示与基线文档

```text
docs/演示指南.md
docs/已知问题与后续优化.md
docs/版本记录.md
docs/MVP验收报告.md
```

## 下一步建议

下一步建议进入第 9 阶段：在线接口文档 URL 导入与 AI 辅助解析。

- 第 9 阶段：在线接口文档 URL 导入与 AI 辅助解析
- 第 10 阶段：真实 AI 大模型接入
- 第 11 阶段：接口依赖关系与链路用例
- 第 12 阶段：鉴权、token、cookie 增强
- 第 13 阶段：报告和失败分析增强
- 第 14 阶段：CI/CD、定时任务与权限系统
