# MVP 功能边界

## MVP 第一版做什么

MVP 第一版目标是完成一个可逐步演进的 AI 接口自动化测试平台基础闭环。核心方向包括接口资产管理、接口文档导入解析、测试用例管理、AI mock 用例生成、Pytest + Requests 执行、测试报告沉淀，以及 Vue3 前端 MVP 页面。

## MVP 第一版不做什么

- 不做 SSO 登录
- 不做复杂权限系统
- 不做 CI/CD
- 不做 Word/PDF 解析
- 不做复杂接口依赖编排
- 不直接接入生产级真实 AI 流程
- 不让 AI 直接生成自由 Python 代码
- 不做 token/cookie 自动补全
- 不做并发压测
- 不做复杂 Allure 报告
- 不做 WebSocket 实时日志
- 不做生产级复杂前端交互和可视化编排

## 第一阶段已完成什么

- 项目目录结构
- FastAPI 后端基础工程
- MySQL 初始化 SQL
- 9 张 MVP 核心表
- SQLAlchemy models
- Alembic 基础配置
- `.env.example`
- 统一响应格式
- 统一异常处理
- 基础日志配置
- `GET /api/v1/health` 健康检查接口
- 基础文档

## 第二阶段已完成什么

- 项目管理 CRUD
- 环境管理 CRUD
- 接口资产查询、详情、基础信息修改、启用 / 禁用
- 测试用例 CRUD
- 对应 schemas、repositories、services、api 路由
- 基础 API 测试

## 第三阶段已完成什么

- Swagger/OpenAPI JSON 内容导入
- Swagger/OpenAPI JSON 文件导入
- Swagger/OpenAPI URL 导入
- curl 文本导入和解析
- 原始文档内容保存到 `api_document`
- 解析后的接口资产保存到 `api_endpoint`
- 解析接口名称、接口分组、请求方法、接口路径、请求头、Query 参数、Path 参数、Body 参数、响应结构、示例请求、示例响应、是否需要鉴权
- `openapi_parser.py`、`swagger_parser.py`、`curl_parser.py`
- 导入解析 API、schemas、repositories、services
- 基础解析测试

## 第四阶段已完成什么

- 在 `backend/app/ai` 下实现 mock `TestcaseGeneratorAgent`
- 输入 `api_endpoint`，输出结构化测试用例 JSON
- 生成 `normal`、`exception`、`boundary`、`auth` 四类用例
- 生成基础请求参数
- 生成 `status_code`、`json_path_equal`、`json_path_not_null`、`json_path_contains` 基础断言规则
- AI 输出经过 schema 校验后再入库
- 生成结果保存到 `test_case`
- mock AI 调用记录保存到 `ai_analysis_record`
- 实现 `POST /api/v1/endpoints/{endpoint_id}/testcases/generate`
- 增加基础生成接口测试

## 第五阶段已完成什么

- 创建 Pytest 工程模板目录 `backend/app/generator/templates/pytest_project`
- 使用 Jinja2 渲染临时 Pytest 工程
- 从数据库读取 project、environment、api_endpoint、test_case
- 将生成工程保存到 `storage/generated/project_{project_id}/execution_{task_id}/`
- 使用 Requests 执行 HTTP 请求
- 支持 GET、POST、PUT、DELETE、PATCH
- 支持 base_url、headers、query params、JSON body、timeout
- 实现 `status_code`、`json_path_equal`、`json_path_not_null`、`json_path_contains`、`response_time` 断言
- 使用 `jsonpath-ng` 读取 JSONPath
- 使用 subprocess 调用 Pytest
- 使用 pytest-html 生成 HTML 报告
- 日志保存到 `storage/logs`
- 报告保存到 `storage/reports`
- 实现 `POST /api/v1/executions/run`
- 写入 `execution_task`、`execution_result`、`test_report`
- 增加基础执行引擎测试

## 第六阶段已完成什么

- 创建 Vue3 + TypeScript + Vite 前端工程
- 接入 Element Plus、Vue Router、Pinia、Axios
- 创建统一 Axios 请求封装，默认 baseURL 为 `/api/v1`
- 创建顶部 Header、左侧菜单、主内容区和面包屑
- 实现项目管理页
- 实现环境配置页
- 实现接口文档导入页
- 实现接口列表页
- 实现接口详情页
- 实现 AI mock 用例生成页，并明确当前为 mock AI 用例生成
- 实现测试用例管理页
- 实现执行结果 / 测试报告页
- 增加 `frontend/.env.example`
- 增加前端 TypeScript 类型定义
- 通过前端类型检查和构建验证

## 第七阶段已完成什么

- 完成第 1-6 阶段 MVP 功能联调验收
- 验证后端服务、前端服务和健康检查接口
- 实际执行 MySQL 初始化 SQL
- 验证 9 张核心表存在
- 使用 `examples/mvp_acceptance/openapi_health.json` 作为验收测试数据
- 跑通项目创建、环境配置、OpenAPI 导入、接口资产保存、接口详情查看、AI mock 用例生成、测试用例编辑 / 禁用、Pytest + Requests 执行、执行结果保存、测试报告保存和前端报告页访问
- 修复 Vite 代理规则过宽导致 `/api-import` 路由被代理到后端的问题
- 新增 `docs/MVP验收报告.md`

## 第八阶段已完成什么

- 固化当前 MVP 基线为 `v0.1.0-mvp`
- 补充当前 MVP 已完成、可演示、可继续迭代的统一说明
- 新增 `docs/演示指南.md`
- 新增 `docs/已知问题与后续优化.md`
- 新增 `docs/版本记录.md`
- 补充 `docs/MVP验收报告.md` 的 MVP 结论、限制和后续方向
- 明确“在线接口文档 URL 导入与 AI 辅助解析”放到第 9 阶段

## 当前仍未实现什么

- 未接真实 AI
- 未实现真实大模型调用
- 未支持输入 Knife4j / Swagger UI 的 `doc.html` 页面地址并自动解析
- 未实现在线接口文档 URL 导入与 AI 辅助解析
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

## 后续阶段如何演进

第八阶段已完成，当前 MVP 已固化为 `v0.1.0-mvp`。后续建议：

- 第 9 阶段：在线接口文档 URL 导入与 AI 辅助解析
- 第 10 阶段：真实 AI 大模型接入
- 第 11 阶段：接口依赖关系与链路用例
- 第 12 阶段：鉴权、token、cookie 增强
- 第 13 阶段：报告和失败分析增强
- 第 14 阶段：CI/CD、定时任务与权限系统
