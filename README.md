# Knowledge Agent

企业知识库 Agent，目标是在 3 个月内完成一个可以演示、可以部署、可以写进简历的 RAG + Agent 项目。

## 项目目标

- 支持上传 PDF、txt、markdown 文档。
- 解析文档并切分为 chunks。
- 使用 Chroma 保存 embedding 向量并进行相似度检索。
- 使用 MySQL 保存文档元数据、会话、消息、调用日志和评测结果。
- 基于 RAG 回答问题，并展示引用来源。
- 支持 tool calling、权限确认、trace 日志和评测集。

## 技术栈

- Python
- FastAPI
- MySQL
- Chroma
- SQLAlchemy
- LLM API
- Docker

## 本地运行

创建虚拟环境：

```powershell
python -m venv .venv
```

激活虚拟环境：

```powershell
.\.venv\Scripts\Activate.ps1
```

安装依赖：

```powershell
pip install -r requirements.txt
```

启动服务：

```powershell
uvicorn app.main:app --reload
```

启动后访问：

- API 首页：http://127.0.0.1:8000
- 健康检查：http://127.0.0.1:8000/health
- 接口文档：http://127.0.0.1:8000/docs

## 当前进度

- [x] Day 1：项目骨架
- [ ] Day 2：FastAPI 路由和 `/api/chat` 空接口
- [ ] Day 3：Pydantic 请求响应模型
- [ ] Day 4：MySQL 连接和基础表设计

