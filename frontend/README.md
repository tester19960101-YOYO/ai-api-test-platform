# Frontend README

## 前端简介

这是 AI API Test Platform / AI 接口自动化测试平台的前端工程。当前已完成 Vue3 前端 MVP 页面，并在第 9 阶段增强接口导入页。

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
