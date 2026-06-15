# AI API Test Platform

AI API Test Platform / AI 接口自动化测试平台，用于管理接口资产、导入和解析接口文档、使用 mock AI 生成结构化接口测试用例，并通过 Pytest + Requests 执行接口自动化测试。

当前 MVP 主流程已跑通并固化为 `v0.1.0-mvp`。第 9 阶段已完成“多形态接口输入导入与 AI 辅助解析”，并收尾标记为 `v0.1.0-stage9`。第 10 阶段已完成“鉴权配置与业务断言增强”，当前版本适合演示和继续迭代。

## 当前阶段

已完成第 1-10 阶段：

- 第 1 阶段：项目骨架、后端基础工程、数据库表、SQLAlchemy models、健康检查、基础文档。
- 第 2 阶段：项目、环境、接口资产、测试用例基础 CRUD。
- 第 3 阶段：Swagger/OpenAPI JSON、文件、URL 和 curl 导入解析。
- 第 4 阶段：mock AI 用例生成。
- 第 5 阶段：Pytest + Requests 基础执行引擎。
- 第 6 阶段：Vue3 前端 MVP 页面。
- 第 7 阶段：MVP 联调验收与缺陷修复。
- 第 8 阶段：MVP 基线固化与演示准备，版本为 `v0.1.0-mvp`。
- 第 9 阶段：多形态接口输入导入与 AI 辅助解析。
- 第 10 阶段：鉴权配置与业务断言增强。

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

- 9 张 MVP 核心表：`project`、`environment`、`api_document`、`api_endpoint`、`test_case`、`execution_task`、`execution_result`、`test_report`、`ai_analysis_record`
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
- mock AI 用例生成，AI 输出仅为结构化 JSON
- Pytest + Requests 执行引擎、pytest-html 报告、执行日志
- Vue3 前端 MVP 页面和接口联调入口
- 执行报告页支持多选测试用例执行，并可展开单条结果查看请求参数 JSON、响应体 JSON 和 curl 命令，支持复制
- 环境配置支持 `auth_type`、`token`、`cookie`、公共 headers、`auth_config_json`、timeout 和 retry 配置
- 执行测试时自动合并环境公共 headers、环境鉴权 headers 和用例请求 headers
- 业务断言支持 `business_code`、`business_success`、`json_path_not_empty`，并对响应 JSON 中的 `code` / `success` 提供默认业务断言兜底
- 执行结果保存脱敏后的请求数据、响应体、curl 命令和断言结果，避免在报告中暴露完整 token / cookie

## 暂未实现内容

- 未接真实大模型，当前仍为 mock AI
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
- 保存后的接口资产会继续用于 AI mock 测试用例生成。
- AI 只做 mock 辅助提示，不凭空编造接口参数。
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
11. 选择接口生成 mock AI 测试用例。
12. 管理测试用例。
13. 在执行报告页多选测试用例并执行测试。
14. 展开单条执行结果，查看并复制请求参数 JSON、响应体 JSON 和 curl 命令。
15. 查看执行结果和 pytest-html 报告。

## 下一阶段建议

- 第 11 阶段：真实 AI 大模型接入
- 第 12 阶段：接口依赖关系与链路用例
- 第 13 阶段：报告和失败分析增强
- 第 14 阶段：CI/CD、定时任务与权限系统
