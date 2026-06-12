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
- 复杂接口依赖、token 刷新、权限、多用户协作、生产部署暂未实现。

## 后续阶段

- 第 10 阶段：真实 AI 大模型接入
- 第 11 阶段：接口依赖关系与链路用例
- 第 12 阶段：鉴权、token、cookie 增强
- 第 13 阶段：报告和失败分析增强
- 第 14 阶段：CI/CD、定时任务与权限系统
