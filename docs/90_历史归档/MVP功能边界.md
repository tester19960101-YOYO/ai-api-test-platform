⚠️ 已归档，仅用于历史参考

# MVP 功能边界

## MVP 第一版做什么

MVP 第一版实现一个可演示、可继续迭代的 AI 接口自动化测试平台闭环：

- 项目管理
- 环境配置
- 接口文档导入与解析
- 接口资产管理
- mock AI 用例生成
- 测试用例管理
- Pytest + Requests 执行
- 执行结果与测试报告查看
- Vue3 前端 MVP 页面

## MVP 第一版不做什么

- 不接真实大模型
- 不让 AI 直接生成自由 Python 代码
- 不根据 HTML 页面凭空编造接口参数
- 不做复杂接口依赖编排
- 不做复杂 token/cookie 自动刷新
- 不做 Word/PDF 解析
- 不做权限系统、SSO、多用户协作
- 不做 CI/CD、定时任务
- 不做 WebSocket 实时日志
- 不做生产级部署方案

## 已完成阶段

- 第 1 阶段：项目骨架、后端基础工程、数据库表、SQLAlchemy models、健康检查、基础文档。
- 第 2 阶段：项目、环境、接口资产、测试用例基础 CRUD。
- 第 3 阶段：Swagger/OpenAPI JSON、文件、URL 和 curl 导入解析。
- 第 4 阶段：mock AI 用例生成，写入 `test_case` 和 `ai_analysis_record`。
- 第 5 阶段：Pytest + Requests 执行引擎，写入 `execution_task`、`execution_result`、`test_report`。
- 第 6 阶段：Vue3 前端 MVP 页面。
- 第 7 阶段：MVP 联调验收。
- 第 8 阶段：MVP 固化为 `v0.1.0-mvp`。
- 第 9 阶段：多形态接口输入导入与 AI 辅助解析。
- 第 10 阶段：鉴权配置与业务断言增强。
- 第 10.1 阶段：断言系统 2.0，完成 AI 建议、Swagger 基础断言、用户断言的融合执行，并上线 DSL 可视化断言编辑器。

## 第 9 阶段已完成内容

- 支持在线 OpenAPI/Swagger JSON URL。
- 支持 Knife4j / Swagger UI 页面地址自动发现真实接口文档 JSON。
- 支持候选地址：`/v3/api-docs`、`/v2/api-docs`、`/swagger-resources`、`/api-docs`、`/openapi.json`、`/swagger.json`。
- 支持单接口文档页面 URL 的 hash hint 提取和接口筛选。
- 支持接口路径、请求方法、名称、分组、关键词筛选。
- 支持 Swagger/OpenAPI JSON 内容。
- 保留 curl 文本导入能力。
- 支持仅预览、保存选中接口、保存全部接口。
- 未找到接口资产时只创建待完善接口草稿。
- 前端接口导入页支持预览列表、勾选、编辑确认和保存。
- 支持 OpenAPI / Swagger 基础 `$ref` 展开。
- 支持参数 JSON、Body JSON、响应 JSON 的“展开示例 / 展开 Schema”切换。
- 支持用户编辑预览 JSON 后保存接口资产。
- 保存后的接口资产可继续用于 AI mock 测试用例生成。

## 当前限制

- AI 仍为 mock，不接真实大模型。
- AI 辅助解析只做提示和边界控制，不从 HTML 页面凭空生成完整接口结构。
- 已支持环境级 token、cookie、header 配置和执行时自动携带，但复杂 token 自动刷新、登录态自动获取、SSO、验证码、权限、多用户协作、生产部署暂未实现。

## 第 10 阶段已完成内容

- 环境配置页支持鉴权类型、Token、Cookie、Header JSON、`auth_config_json`、timeout 和 retry 配置。
- 执行引擎读取环境配置，自动合并环境公共 headers、环境鉴权 headers 和测试用例请求 headers。
- 请求头合并优先级为：环境公共 headers < 环境鉴权 headers < 测试用例请求 headers。
- 支持基础重试次数配置。
- 业务断言支持 `business_code`、`business_success`、`json_path_not_empty`。
- 当响应 JSON 包含 `code` 或 `success` 且用例未显式断言时，执行引擎会自动增加默认业务断言，避免 HTTP 200 但业务失败被误判为通过。
- 执行结果保存请求参数、响应体、curl 命令和断言结果。
- 执行报告页展示断言结果，并继续支持请求参数、响应体、curl 展开和复制。
- 报告与日志中不保存完整 token / cookie，仅保存脱敏后的请求头和 curl。

## 第 10.1 阶段已完成内容

- 新增 `backend/app/core/assertion_engine_v2.py` 断言融合引擎。
- 统一断言结构，支持 `source`、`type`、`path`、`operator`、`expected`、`priority`、`enabled`。
- 支持三层断言来源：用户断言、Swagger/OpenAPI 基础断言、mock AI 断言建议。
- 断言融合优先级为：用户断言 > Swagger/OpenAPI 断言 > AI 建议断言。
- 同一路径断言去重时保留最高优先级断言，最终执行结果可追溯断言来源。
- `business_code` 不再写死为 1，改为支持 `success_codes` 或 `success_expression`。
- `$.data` 相关 JSONPath 校验仅在业务成功后执行，避免 401/500 或业务失败时误判。
- mock AI 只生成带 `confidence` 的结构化断言建议，默认不控制 pass/fail。
- 测试用例页面可查看 AI 断言建议、Swagger 断言、用户断言和最终融合断言预览。
- 接口详情页可查看 Swagger 基础断言预览。
- 新增断言 DSL 可视化系统，用户不再手写 JSON 断言。
- DSL 支持 `$.code == 200`、`$.data != null`、`status_code == 200`、`$.msg contains 成功`。
- 支持 `==`、`!=`、`>`、`<`、`contains`、`exists`、`not null`。
- AI / Swagger / 用户断言统一展示为 DSL，JSON 只在后端执行层内部使用。
- 新增 DSL 解析和 JSON 转 DSL 接口。

## 后续阶段

- 第 11 阶段：真实 AI 大模型接入
- 第 12 阶段：接口依赖关系与链路用例
- 第 13 阶段：报告和失败分析增强
- 第 14 阶段：CI/CD、定时任务与权限系统
