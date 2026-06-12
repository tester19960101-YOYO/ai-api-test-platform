# Frontend README

## 前端简介

这是 AI API Test Platform / AI 接口自动化测试平台的前端工程。当前已完成第六阶段 Vue3 前端 MVP 页面，第七阶段完成 MVP 联调验收，第八阶段固化 MVP 基线为 `v0.1.0-mvp`。前端用于通过页面完成项目管理、环境配置、接口导入、接口查看、AI mock 用例生成、测试用例管理、执行测试和查看报告。

## 当前阶段说明

当前前端实现状态是 Vue3 前端 MVP 页面，当前 MVP 版本为 `v0.1.0-mvp`。

已完成：

- Vue3 + TypeScript + Vite 工程
- Element Plus
- Vue Router
- Pinia
- Axios 统一请求封装
- 基础布局
- MVP 页面

当前不做：

- 当前仍为 mock AI，不接真实 AI
- 不实现登录和权限系统
- 不实现复杂用例编排
- 不实现 WebSocket 实时日志
- 不在前端直接连接 MySQL
- 不在前端直接执行 Pytest
- 不在前端直接请求被测接口

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

开发环境默认使用 Vite proxy，将 `/api/v1` 转发到后端：

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

默认访问：

```text
http://127.0.0.1:5173/
```

## 构建与类型检查

```bash
cd frontend
npm run type-check
npm run build
```

## 页面规划与实现状态

已实现页面：

- 项目管理页
- 环境配置页
- 接口文档导入页
- 接口列表页
- 接口详情页
- AI 用例生成页
- 测试用例管理页
- 执行结果 / 测试报告页

## 路由列表

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

## 目录结构

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
