from pydantic import BaseModel


class ChatRequest(BaseModel):
    """请求体结构"""
    message: str


class ChatSource(BaseModel):
    """相关文档结构"""
    chunk_id: int
    document_id: int
    chunk_index: int
    content: str


class ChatResponse(BaseModel):
    """响应体结构"""
    reply: str
    session_id: int
    user_message_id: int
    assistant_message_id: int
    latency_ms: int
    sources: list[ChatSource]

