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

## 文档上传和解析验证

项目自带 3 个测试文档：

| 文件 | 用途 |
| --- | --- |
| `tests/fixtures/sample.pdf` | 验证 PDF 上传和 `pypdf` 文本抽取 |
| `tests/fixtures/sample.txt` | 验证 txt 上传和文本解析 |
| `tests/fixtures/sample.md` | 验证 markdown 上传和文本解析 |

启动服务后，打开接口文档：

```txt
http://127.0.0.1:8000/docs
```

在 `POST /api/documents/upload` 中选择测试文档上传。成功时会返回：

```json
{
  "document_id": 1,
  "filename": "sample.pdf",
  "content_type": "application/pdf",
  "file_path": "storage\\uploads\\sample.pdf",
  "page_count": 1
}
```

然后可以用文档管理接口验证数据库记录：

| 接口 | 作用 |
| --- | --- |
| `GET /api/documents` | 查看所有已上传文档 |
| `GET /api/documents/{document_id}` | 查看单个文档元数据 |
| `DELETE /api/documents/{document_id}` | 删除单个文档数据库记录 |

当前上传限制：

- 只支持 `.pdf`、`.txt`、`.md`、`.markdown`。
- 文件不能超过 10MB。
- 空文件会被拒绝。
- 没有可解析文本的文件会被拒绝。

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
  -> 检查文件后缀，只允许 .pdf、.txt、.md、.markdown
  -> 读取文件内容，拒绝空文件，并限制最大 10MB
  -> 保存到 storage/uploads/
  -> app/services/document_parser.py 的 parse_document() 统一解析文档
  -> 解析失败或没有可解析文本时返回清楚错误
  -> app/services/text_splitter.py 的 split_pages() 切分 chunks
  -> app/services/document.py 的 DocumentService 保存文档元数据
  -> 保存 chunks 到 PostgreSQL
  -> 返回 document_id、filename、content_type、file_path、page_count、chunk_count
```

关键点：

| 名称 | 作用 |
| --- | --- |
| `UploadFile` | FastAPI 用来接收上传文件 |
| `python-multipart` | 解析 `multipart/form-data` 文件上传请求 |
| `Path("storage/uploads")` | 表示文件保存目录 |
| `file.file.read()` | 读取上传文件内容 |
| `write_bytes()` | 把二进制内容写入本地文件 |
| `parse_document()` | 根据文件后缀选择 PDF 或文本解析方式 |
| `split_pages()` | 把解析后的页文本切成 chunks |
| `PdfReader` | pypdf 用来读取 PDF 结构 |
| `page.extract_text()` | 抽取某一页的文本 |
| `HTTPException` | 主动返回清楚的接口错误 |
| `page_count` | 当前 PDF 的页数 |
| `chunk_count` | 当前文档保存的 chunk 数量 |
| `DocumentService` | 保存文档元数据到 PostgreSQL |
| `document_id` | 数据库生成的文档记录 ID |

### 文档管理接口

当前支持 3 个文档管理接口：

| 接口 | 作用 |
| --- | --- |
| `GET /api/documents` | 返回所有文档元数据 |
| `GET /api/documents/{document_id}` | 根据 ID 返回单个文档 |
| `GET /api/documents/{document_id}/chunks` | 查询某篇文档的 chunks |
| `DELETE /api/documents/{document_id}` | 根据 ID 删除文档数据库记录 |

接口分层：

```txt
app/api/documents.py
  -> 接收 HTTP 请求，处理 404 等接口错误
app/services/document.py
  -> list_documents() 查询文档列表
  -> get_document() 查询单个文档
  -> list_chunks() 查询某篇文档的 chunks
  -> delete_document() 删除文档记录和对应 chunks
app/schemas/document.py
  -> DocumentResponse 定义文档响应格式
  -> ChunkResponse 定义 chunk 响应格式
```

### 文本切分流程

解析后的文档页会继续切成 chunks，供后续 embedding 和检索使用。

```txt
app/services/document_parser.py
  -> parse_document() 返回 page_number + text
app/services/text_splitter.py
  -> split_text() 按 chunk_size 和 overlap 切分一段文本
  -> split_pages() 把多页文本切成带 page_number、chunk_index、content 的 chunks
```

关键概念：

| 名称 | 作用 |
| --- | --- |
| `chunk_size` | 每个 chunk 的最大字符数 |
| `overlap` | 相邻 chunk 重叠的字符数，用来保留上下文 |
| `chunk_index` | chunk 在整篇文档中的顺序 |

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
- [x] Day 10：文档元数据保存到 PostgreSQL
- [x] Day 11：文档列表、详情和删除接口
- [x] Day 12：txt 和 markdown 文件解析
- [x] Day 13：解析失败、空文件和无可解析文本处理
- [x] Day 14：README 增加文档上传和解析说明，准备测试文档
- [x] Day 15：文本切分 chunk size 和 overlap
- [x] Day 16：保存 chunk 元数据和原文到 PostgreSQL
- [ ] Day 17：接入 embedding API
