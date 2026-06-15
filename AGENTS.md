# AGENTS.md

## 项目定位

AI API Test Platform / AI 接口自动化测试平台，用于管理接口资产、导入和解析接口文档、使用 mock AI 生成结构化接口测试用例，并通过 Pytest + Requests 执行接口自动化测试，沉淀执行结果和测试报告。

当前已完成第一阶段到第 10.1 阶段，MVP 基线版本为 `v0.1.0-mvp`，第 9 阶段收尾版本标记为 `v0.1.0-stage9`，第 10 阶段归档版本为 `v0.10.0`：

- 第一阶段：项目骨架、后端基础工程、数据库表设计、SQLAlchemy models、健康检查接口、基础配置和基础文档。
- 第二阶段：项目、环境、接口资产、测试用例的后端基础 CRUD。
- 第三阶段：Swagger/OpenAPI 和 curl 的导入解析，并将解析结果保存到 `api_document` 和 `api_endpoint`。
- 第四阶段：AI mock 用例生成，生成结构化测试用例 JSON，保存到 `test_case`，并保存 mock AI 调用记录到 `ai_analysis_record`。
- 第五阶段：Pytest + Requests 基础执行引擎，生成临时测试工程，执行测试用例，保存 `execution_task`、`execution_result` 和 `test_report`。
- 第六阶段：Vue3 前端 MVP 页面，完成项目管理、环境配置、接口导入、接口列表、接口详情、AI mock 用例生成、测试用例管理、执行结果 / 测试报告页面。
- 第七阶段：MVP 联调验收与缺陷修复，完成第 1-6 阶段主流程验收并新增 `docs/MVP验收报告.md`。
- 第八阶段：MVP 基线固化与演示准备，完成演示指南、已知问题、后续路线和版本记录，当前标记为 `v0.1.0-mvp`。
- 第九阶段：多形态接口输入导入与 AI 辅助解析，完成在线 OpenAPI/Swagger URL、Knife4j / Swagger UI 文档发现、Cookie 抓取、单接口页面 hint 筛选、JSON 预览编辑和执行报告页增强。
- 第十阶段：鉴权配置与业务断言增强，完成环境级 token/cookie/header 配置、执行请求头合并、业务断言兜底和执行报告断言结果展示。
- 第 10.1 阶段：断言系统2.0融合引擎，完成 AI 建议层、Swagger 基础层、用户最高优先级断言融合和来源追踪。

## 技术栈

- 前端：Vue3 + TypeScript + Vite + Element Plus
- 后端：FastAPI + SQLAlchemy + Alembic + Pydantic
- 数据库：MySQL 8.0
- 执行引擎：Pytest + Requests
- 辅助库：Jinja2、PyYAML、jsonpath-ng、pytest-html

## 后端目录规范

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
      router.py
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
```

## 前端目录规范

```text
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
```

前端规范：

- 前端使用 Vue3 + TypeScript + Vite + Element Plus。
- API 请求统一放在 `frontend/src/api`。
- 路由统一放在 `frontend/src/router`。
- Pinia store 放在 `frontend/src/stores`。
- TypeScript 类型定义放在 `frontend/src/types`。
- 页面放在 `frontend/src/views`。
- 组件放在 `frontend/src/components`。
- 布局放在 `frontend/src/layouts`。
- 前端不直接连接 MySQL。
- 前端不直接执行 Pytest。
- 前端不直接请求被测接口，所有操作都通过后端 API 完成。

## AI 模块规范

- AI 模块位置固定为 `backend/app/ai`。
- 当前 AI 用例生成是 mock 实现，不接真实 AI，不调用 OpenAI、Qwen 或其他真实模型。
- AI 不直接生成自由 Python 代码。
- AI 只生成结构化 JSON。
- AI 输出必须经过 schema 校验后再入库。
- 生成的测试用例保存到 `test_case`。
- mock AI 调用记录保存到 `ai_analysis_record`。
- 后续真实 AI 接入时必须复用统一模块结构和结构化输出边界。

## 自动化测试代码生成规范

- 执行引擎采用 Pytest + Requests。
- Pytest 工程模板位置固定为 `backend/app/generator/templates/pytest_project`。
- 生成出来的测试工程位置固定为 `storage/generated/project_{project_id}/execution_{task_id}/`。
- 上传文件位置固定为 `storage/uploads`。
- 测试报告位置固定为 `storage/reports/execution_{task_id}/report.html`。
- 执行日志位置固定为 `storage/logs/execution_{task_id}/pytest.log`。
- 生成出来的测试代码不要放进 `backend/app`。
- Pytest 代码通过模板生成，不由 AI 直接自由生成。

## 数据库规范

数据库使用 MySQL 8.0，表使用 InnoDB 和 utf8mb4。

核心表固定为：

1. `project`
2. `environment`
3. `api_document`
4. `api_endpoint`
5. `test_case`
6. `execution_task`
7. `execution_result`
8. `test_report`
9. `ai_analysis_record`

数据库规范：

- 主键统一使用 `BIGINT AUTO_INCREMENT`。
- 所有核心表必须包含 `created_at` 和 `updated_at`。
- 复杂结构字段使用 JSON 类型。
- 表和字段必须添加 COMMENT。
- 表结构变更必须同步更新 `database/init.sql`、`backend/app/models` 和 `docs/数据库表设计.md`。

## 代码规范

- API 路由统一挂载在 `backend/app/api/router.py`。
- v1 接口统一放在 `backend/app/api/v1`。
- 配置放在 `backend/app/core/config.py`。
- 数据库连接放在 `backend/app/db/session.py`。
- SQLAlchemy models 放在 `backend/app/models`。
- schemas 放在 `backend/app/schemas`。
- repositories 放在 `backend/app/repositories`。
- services 放在 `backend/app/services`。
- generator 放在 `backend/app/generator`。
- runner 放在 `backend/app/runner`。
- 不要把密钥、密码、Token 写进源码，使用环境变量和 `.env`。
- 不要把生成出来的测试工程提交到后端应用代码目录。

## 验证要求

基础验证至少包括：

```bash
cd backend
pip install -r requirements.txt
python -m compileall app
python -m pytest
uvicorn app.main:app --reload
curl http://127.0.0.1:8000/api/v1/health
```

前端阶段验证至少包括：

```bash
cd frontend
npm install
npm run type-check
npm run build
npm run dev
```

执行引擎阶段还需要确认：

- `POST /api/v1/executions/run` 路由已注册。
- generator 模块可以正常 import。
- runner 模块可以正常 import。
- 生成工程位于 `storage/generated`。
- 生成出来的测试代码没有写入 `backend/app`。
- Pytest 可以实际执行。
- `execution_task`、`execution_result`、`test_report` 可以正常写入。

## 阶段开发完成标准

以后每完成一个阶段，都必须自动执行以下流程。不要等用户单独提醒。

### 1. 先读取项目上下文

在开始阶段开发前，必须先读取：

- `AGENTS.md`
- `README.md`
- `docs/MVP功能边界.md`
- 与当前阶段相关的 docs 文档

例如：

- 后端 CRUD 阶段需要读取 `docs/后端接口设计.md`
- 接口导入阶段需要读取 `docs/后端接口设计.md` 和 `docs/数据库表设计.md`
- AI 阶段需要读取 `docs/AI能力设计.md`
- 执行引擎阶段需要读取 `docs/执行引擎设计.md`
- 前端阶段需要读取 `docs/前端页面设计.md` 和 `frontend/README.md`

### 2. 严格控制当前阶段范围

每个阶段只实现当前阶段要求的功能，不要提前开发后续阶段功能。

如果发现某个功能属于后续阶段，只能预留目录或接口说明，不要提前实现。

### 3. 开发完成后必须自行验证

每个阶段开发完成后，必须根据实际阶段运行验证命令。

基础验证包括：

- Python 语法检查
- 后端服务启动检查
- 健康检查接口访问
- 相关模块 import 检查
- 新增 API 的接口验证
- 数据库变更检查
- 如有测试用例，需要运行测试

如果当前环境无法完成某项验证，必须明确说明原因，并提供本地验证命令。

不要假装验证通过。

### 4. 开发完成后必须更新相关文档

每个阶段完成后，必须根据实际实现内容更新文档。

每阶段都需要检查并按需更新：

- `README.md`
- `docs/MVP功能边界.md`

按阶段更新对应文档：

第二阶段：后端基础 CRUD

- `docs/后端接口设计.md`
- `README.md`
- `docs/MVP功能边界.md`
- `backend/README.md`

第三阶段：接口文档导入与解析

- `docs/后端接口设计.md`
- `docs/MVP功能边界.md`
- `README.md`
- 如数据库结构变化，同步更新 `docs/数据库表设计.md` 和 `database/init.sql`

第四阶段：AI mock 用例生成

- `docs/AI能力设计.md`
- `docs/后端接口设计.md`
- `README.md`
- `docs/MVP功能边界.md`
- 如 `ai_analysis_record` 或 `test_case` 使用方式变化，同步更新 `docs/数据库表设计.md`

第五阶段：Pytest + Requests 执行引擎

- `docs/执行引擎设计.md`
- `docs/后端接口设计.md`
- `README.md`
- `docs/MVP功能边界.md`
- 如 `execution_task`、`execution_result`、`test_report` 使用方式变化，同步更新 `docs/数据库表设计.md`
- 如执行命令或生成目录规范变化，同步更新 `AGENTS.md`

第六阶段：Vue3 前端 MVP 页面

- `docs/前端页面设计.md`
- `README.md`
- `frontend/README.md`
- `docs/MVP功能边界.md`

### 5. AGENTS.md 不是每次都必须改

`AGENTS.md` 只有在以下情况才需要更新：

- 技术栈变化
- 目录结构变化
- 开发规范变化
- 验证命令变化
- 生成代码位置变化
- AI 使用边界变化
- Codex 后续需要新增固定约束

否则不要频繁修改 `AGENTS.md`。

### 6. 文档内容必须和代码保持一致

文档中不能写未实现功能。

如果功能只是预留目录，必须明确写：

```text
已预留，暂未实现
```

如果功能已经实现，必须说明：

- 实现位置
- API 路径
- 数据库表
- 启动或验证方式
- 当前限制

### 7. 每个阶段完成后必须做文档一致性检查

需要检查：

- 技术栈是否一致
- 目录路径是否一致
- 阶段范围是否一致
- 已完成功能是否一致
- 未实现功能是否一致
- API 路径是否一致
- 数据库表名称是否一致
- 下一阶段计划是否一致
- `README.md`、`AGENTS.md`、`docs` 文档之间是否存在冲突

如发现不一致，必须修正后再输出最终结果。

### 8. 每个阶段最终输出格式

每个阶段完成后，最终必须输出：

1. 本阶段完成了什么
2. 新增/修改的代码文件
3. 新增/修改的文档文件
4. 数据库是否有变更
5. API 是否有新增或变更
6. 已执行的验证命令
7. 每条验证命令的结果
8. 是否存在未完成或受环境限制的验证
9. 文档一致性检查结果
10. 下一阶段建议

### 9. 禁止事项

每个阶段禁止：

- 不验证就说完成
- 文档写未实现功能
- 代码和文档描述不一致
- 把生成出来的测试工程放进 `backend/app`
- 让 AI 直接生成自由 Python 代码并运行
- 提前开发后续阶段功能
- 隐瞒环境限制或验证失败

## 不要做的事情

- 当前不要接真实 AI。
- 当前不要调用 OpenAI、Qwen 或其他真实模型。
- 当前不要让 AI 生成自由 Python 代码。
- 当前不要实现复杂接口依赖编排。
- 当前不要实现复杂 token 自动刷新。
- 当前不要实现权限系统、SSO 登录、CI/CD。
- 当前不要实现 Word/PDF 解析。
- 当前不要实现 httpx 异步执行。
- 当前不要实现并发压测。
- 当前不要实现 WebSocket 实时日志。
- 当前不要实现生产级复杂前端交互和可视化编排。
