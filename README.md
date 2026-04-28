# Knowledge Agent

企业知识库 Agent，目标是在 3 个月内完成一个可以演示、可以部署、可以写进简历的 RAG + Agent 项目。

## 学习方式

本项目采用“教练模式”推进：先讲最小概念，再由学习者亲自完成小任务，随后 review、纠错和总结。

后续 AI/Codex 助手请先阅读 [AGENTS.md](AGENTS.md)，不要默认直接代写完整功能。

## 项目目标

- 支持上传 PDF、txt、markdown 文档。
- 解析文档并切分为 chunks。
- 使用 PostgreSQL 保存文档元数据、会话、消息、调用日志和评测结果。
- 后续使用 pgvector 保存 embedding 向量并进行相似度检索。
- 基于 RAG 回答问题，并展示引用来源。
- 支持 tool calling、权限确认、trace 日志和评测集。

## 技术栈

- Python
- FastAPI
- Pydantic
- PostgreSQL
- pgvector
- SQLAlchemy
- pydantic-settings + python-dotenv
- OpenAI Python SDK（当前用于 DeepSeek 兼容接口）
- python-multipart（文件上传表单解析）
- pypdf（PDF 文本解析）
- Uvicorn
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

创建 `.env` 文件：

```env
DATABASE_URL=postgresql+psycopg://postgres:你的密码@localhost:5432/knowledge_agent
DEEPSEEK_API_KEY=你的 DeepSeek API Key
```

启动服务：

```powershell
python -m uvicorn app.main:app --reload
```

如果虚拟环境启动器路径异常，可以使用更稳的写法：

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

启动后访问：

- API 首页：http://127.0.0.1:8000
- 健康检查：http://127.0.0.1:8000/health
- 接口文档：http://127.0.0.1:8000/docs

常用验证命令：

```powershell
python -m tests.check_database
python -m tests.create_tables
```

## 当前程序流程

### `/api/chat` 聊天接口

一次聊天请求的流程：

```txt
POST /api/chat
  -> app/api/chat.py 的 chat()
  -> app/schemas/chat.py 的 ChatRequest 校验请求体
  -> app/core/database.py 的 get_db() 提供数据库 Session
  -> app/services/chat.py 的 ChatService 处理聊天业务
  -> app/services/llm.py 的 LLMService 调用大模型
  -> app/models/chat.py 的 ChatSession / ChatMessage 保存会话和消息
  -> app/schemas/chat.py 的 ChatResponse 返回结果
```

关键文件说明：

| 文件 | 作用 |
| --- | --- |
| `app/main.py` | 创建 FastAPI 应用，并挂载路由 |
| `app/api/chat.py` | 定义 `/api/chat` 接口，负责接收请求和调用业务层 |
| `app/schemas/chat.py` | 定义请求和响应格式：`ChatRequest`、`ChatResponse` |
| `app/services/chat.py` | 聊天业务逻辑：创建会话、保存消息、调用 LLM |
| `app/services/llm.py` | 调用 DeepSeek 兼容接口，并计算模型耗时 |
| `app/core/database.py` | 创建数据库连接，并提供 `get_db()` |
| `app/models/chat.py` | 定义聊天相关数据库表：`ChatSession`、`ChatMessage` |

### `/api/documents/upload` 文档上传接口

一次 PDF 上传请求的流程：

```txt
POST /api/documents/upload
  -> app/api/documents.py 的 upload_document()
  -> UploadFile 接收浏览器上传的文件
  -> 检查 content_type，只允许 application/pdf
  -> 读取文件内容，并限制最大 10MB
  -> 保存到 storage/uploads/
  -> app/services/pdf_parser.py 的 extract_pdf_pages() 解析 PDF
  -> 返回 filename、content_type、file_path、page_count
```

关键点：

| 名称 | 作用 |
| --- | --- |
| `UploadFile` | FastAPI 用来接收上传文件 |
| `python-multipart` | 解析 `multipart/form-data` 文件上传请求 |
| `Path("storage/uploads")` | 表示文件保存目录 |
| `file.file.read()` | 读取上传文件内容 |
| `write_bytes()` | 把二进制内容写入本地文件 |
| `PdfReader` | pypdf 用来读取 PDF 结构 |
| `page.extract_text()` | 抽取某一页的文本 |
| `page_count` | 当前 PDF 的页数 |

## 当前进度

- [x] Day 1：项目骨架
- [x] Day 2：FastAPI 路由和 `/api/chat` 空接口
- [x] Day 3：Pydantic 请求响应模型
- [x] Day 4：PostgreSQL 连接和基础表设计
- [x] Day 5：Service 层拆分
- [x] Day 6：LLM API 普通聊天和调用记录
- [x] Day 7：运行说明、复盘和 Git 提交
- [x] Day 8：PDF 上传接口、文件类型限制和本地保存
- [x] Day 9：PDF 文本解析
- [ ] Day 10：文档元数据保存到 PostgreSQL
