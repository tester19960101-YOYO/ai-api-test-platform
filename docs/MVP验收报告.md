# MVP 验收报告

## 1. 验收范围

本次验收覆盖 AI API Test Platform / AI 接口自动化测试平台第 1-6 阶段已实现功能：

- 第一阶段：项目骨架、后端基础工程、数据库表设计、SQLAlchemy models、健康检查接口、基础配置和基础文档。
- 第二阶段：项目、环境、接口资产、测试用例后端基础 CRUD。
- 第三阶段：Swagger/OpenAPI 和 curl 导入解析。
- 第四阶段：AI mock 用例生成。
- 第五阶段：Pytest + Requests 基础执行引擎。
- 第六阶段：Vue3 前端 MVP 页面。

第七阶段完成 MVP 联调验收与缺陷修复。第八阶段完成 MVP 基线固化与演示准备，当前基线版本为 `v0.1.0-mvp`。

当前仍不接真实 AI，不开发复杂依赖编排、权限系统、登录系统、CI/CD、WebSocket 实时日志或 MVP 范围外增强功能。

## 2. 验收环境

后端启动方式：

```bash
cd backend
.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

前端启动方式：

```bash
cd frontend
npm run dev
```

数据库配置：

```text
MySQL: 127.0.0.1:3306
DATABASE: ai_api_test_platform
USER: ai_test
ROOT PASSWORD: 123456
```

测试数据来源：

```text
examples/mvp_acceptance/openapi_health.json
```

是否使用本地 mock API：

```text
未新增独立 mock API 服务。本次验收使用本机已启动的后端健康检查接口 GET /api/v1/health 作为被测接口，OpenAPI 示例文件仅用于联调验收。
```

## 3. 验收结果汇总

| 验收项 | 验收结果 | 备注 |
| --- | --- | --- |
| 后端启动 | 通过 | `127.0.0.1:8000` 已监听 |
| 前端启动 | 通过 | `127.0.0.1:5173` 已监听 |
| 数据库初始化 | 通过 | 已执行 `database/init.sql` |
| 9 张核心表 | 通过 | 9 张表均存在 |
| 健康检查 | 通过 | `GET /api/v1/health` 返回 `status: ok` |
| 项目管理 | 通过 | 创建项目 ID：11 |
| 环境配置 | 通过 | 创建环境 ID：7，base_url 为 `http://127.0.0.1:8000` |
| 接口导入 | 通过 | 导入 `examples/mvp_acceptance/openapi_health.json` |
| 接口资产保存 | 通过 | 保存接口资产 ID：7 |
| 接口详情查看 | 通过 | `GET /api/v1/api-endpoints/7` 成功 |
| AI mock 用例生成 | 通过 | 生成 4 条 mock 测试用例 |
| 测试用例保存 | 通过 | `test_case` 中保存 4 条 |
| 测试用例编辑 / 禁用 | 通过 | 编辑 1 条，禁用 1 条 |
| Pytest 工程生成 | 通过 | `storage/generated/project_11/execution_5` |
| 测试执行 | 通过 | Pytest 实际执行，包含 1 条通过和 1 条失败 |
| 执行任务保存 | 通过 | `execution_task` 写入 1 条 |
| 执行结果保存 | 通过 | `execution_result` 写入 2 条 |
| 测试报告保存 | 通过 | `test_report` 写入 1 条 |
| 报告文件保存 | 通过 | `storage/reports/execution_5/report.html` |
| 日志文件保存 | 通过 | `storage/logs/execution_5/pytest.log` |
| 前端页面访问 | 通过 | 8 个 MVP 页面路由均可访问 |
| 前端报告查看 | 通过 | 执行报告页可打开，并识别当前项目 ID：11 |
| 基础错误信息展示 | 通过 | 失败用例保存错误：`expected status_code 400, got 200; expected 400, got 0` |
| 生成代码位置 | 通过 | 生成工程位于 `storage/generated`，未进入 `backend/app` |
| 文档一致性 | 通过 | 已更新阶段状态、代理路径和验收报告 |

## 4. 发现的问题

| 问题描述 | 影响范围 | 修复状态 |
| --- | --- | --- |
| Vite dev server 代理规则使用 `/api`，导致前端路由 `/api-import` 被误代理到后端，直达该路由返回 404。 | 前端接口导入页直达或刷新访问 | 已修复 |
| 当前 PowerShell 进程中 `mysql` 命令未继承 PATH。 | 命令行数据库验证便利性 | 已使用 MySQL CLI 绝对路径完成验证；不属于产品代码问题 |
| `frontend/package.json` 未配置 lint 命令。 | 无法执行 `npm run lint` | 当前阶段按“未配置，跳过”记录；不影响构建和运行 |
| 前端生产构建提示主 chunk 超过 500 kB。 | 构建体积优化 | 暂不处理；不影响 MVP 演示和运行 |

## 5. 已修复问题

- 将 `frontend/vite.config.ts` 的代理规则从 `/api` 收窄为 `/api/v1`。
- 同步更新 `README.md`、`frontend/README.md`、`docs/前端页面设计.md` 中的 Vite proxy 描述。
- 更新 `README.md`、`AGENTS.md`、`backend/README.md`、`docs/MVP功能边界.md`、`docs/AI能力设计.md`、`docs/执行引擎设计.md` 的第七阶段验收状态。

## 6. 未解决问题或限制

- 当前仍是 mock AI，未接真实大模型。
- 未支持输入 Knife4j / Swagger UI 的 `doc.html` 页面地址并自动解析。
- 未实现在线接口文档 URL 导入与 AI 辅助解析，该能力放到第 9 阶段。
- 当前不做复杂接口依赖编排。
- 当前不做复杂 token 自动刷新。
- 当前不做 Word/PDF 解析。
- 当前不做权限系统、登录系统、多用户协作、多租户或 SSO。
- 当前不做 CI/CD。
- 当前不做 WebSocket 实时日志。
- 当前不提供生产级部署方案。
- 当前执行引擎使用 Pytest + Requests，同步执行，不引入 httpx 异步执行。
- 当前报告使用 pytest-html，不引入复杂 Allure 报告。
- 前端未配置 lint 命令，因此未执行 `npm run lint`。
- 当前 PowerShell 进程未继承 `mysql` PATH，数据库验证使用 `C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe` 绝对路径完成。

后续建议迭代方向：

- 第 9 阶段：在线接口文档 URL 导入与 AI 辅助解析。
- 第 10 阶段：真实 AI 大模型接入。
- 第 11 阶段：接口依赖关系与链路用例。
- 第 12 阶段：鉴权、token、cookie 增强。
- 第 13 阶段：报告和失败分析增强。
- 第 14 阶段：CI/CD、定时任务与权限系统。

## 7. MVP 结论

MVP 主流程已跑通。

本次验收完成了从前端页面、后端 API、MySQL 数据库、OpenAPI 导入、接口资产保存、AI mock 用例生成、测试用例保存、Pytest + Requests 执行、执行结果保存、测试报告保存到报告路径展示的基础闭环。

当前 MVP 达到可演示状态，可以进入 MVP 后增强阶段。第八阶段已将当前基线标记为 `v0.1.0-mvp`。
