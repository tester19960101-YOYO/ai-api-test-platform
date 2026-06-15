# Frontend README

## 前端简介

这是 AI API Test Platform / AI 接口自动化测试平台的前端工程。当前已完成 Vue3 前端 MVP 页面，并在第 9 阶段增强接口导入页，在第 10 阶段增强环境配置页和执行报告页，在第 10.1 阶段增加断言系统 2.0 的展示与 DSL 可视化编辑入口。

## 当前阶段说明

当前前端可完成：

- 项目管理
- 环境配置
- 接口导入预览与保存
- 接口资产查看
- mock AI 用例生成
- 测试用例管理
- 执行测试
- 查看执行结果和报告
- 配置环境级 token / cookie / header 鉴权
- 查看业务断言结果和脱敏 curl
- 查看 AI 断言建议、Swagger 断言、用户断言和最终融合断言预览
- 使用 DSL 可视化编辑断言，不再手写 JSON 断言

当前仍为 mock AI，不接真实大模型。

## 技术栈

- Vue3
- TypeScript
- Vite
- Element Plus
- Vue Router
- Pinia
- Axios

## 环境变量

参考 `.env.example`：

```text
VITE_API_BASE_URL=/api/v1
```

开发环境通过 Vite proxy 将 `/api/v1` 转发到：

```text
http://127.0.0.1:8000
```

## 依赖安装

```bash
cd frontend
npm install
```

## 启动方式

```bash
cd frontend
npm run dev
```

访问：

```text
http://127.0.0.1:5173/
```

## 构建验证

```bash
cd frontend
npm run build
```

`npm run build` 会同时执行 TypeScript 类型检查和 Vite 构建。

## 页面列表

- 项目管理页
- 环境配置页
- 接口文档导入页
- 接口列表页
- 接口详情页
- AI 用例生成页
- 测试用例管理页
- 执行结果 / 测试报告页

## 第 10 阶段环境与报告页

环境配置页支持：

- `auth_type`
- Token
- Cookie
- `headers_json`
- `auth_config_json`
- `timeout_seconds`
- `retry_count`

执行报告页支持：

- 多选测试用例执行。
- 展开单条执行结果。
- 查看并复制请求参数 JSON、响应体 JSON、curl 命令和断言结果。
- 使用后端保存的脱敏 curl，不展示完整 token / cookie。

边界：

- 前端不直接请求被测接口。
- 前端不直接执行 Pytest。
- 当前不支持自动 token 刷新、自动登录、验证码、SSO 或浏览器自动化登录。

## 第 10.1 阶段断言系统 2.0 页面增强

测试用例管理页支持：

- 查看 mock AI 断言建议 DSL。
- 查看 Swagger/OpenAPI 基础断言 DSL。
- 使用断言 DSL Builder 新增、删除、编辑和复制用户断言。
- 从模板、AI 建议、Swagger 断言一键插入 DSL。
- 查看最终融合断言预览。

接口详情页支持：

- 查看基于接口响应结构生成的 Swagger/OpenAPI 基础断言预览。

边界：

- 前端仅展示和编辑断言配置，最终融合与执行由后端执行引擎完成。
- mock AI 断言建议不决定测试结果，只有插入到用户断言 DSL 后才参与执行。
- 当前不接入真实 AI 大模型。

## 第 9 阶段接口导入页

支持输入：

- 在线接口文档 URL
- Knife4j / Swagger UI `doc.html` 页面 URL
- 单接口文档页面 URL
- 接口路径
- 请求方法筛选
- 名称、分组、关键词筛选
- Swagger/OpenAPI JSON 内容
- curl 文本

支持操作：

- 仅预览，不保存
- 保存选中接口
- 保存全部接口
- 编辑确认接口基础信息和 JSON 字段

边界：

- 不会导入后自动生成测试用例。
- 测试用例生成必须由用户主动触发。
- 前端不直接连接 MySQL。
- 前端不直接执行 Pytest。
- 前端不直接请求被测接口。
