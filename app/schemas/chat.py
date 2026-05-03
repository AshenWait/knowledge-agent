from datetime import datetime

from pydantic import BaseModel


class ChatRequest(BaseModel):
    """请求体结构"""
    message: str
    document_id: int | None = None
    session_id: int | None = None


class ChatSource(BaseModel):
    """相似文档结构"""
    chunk_id: int
    document_id: int
    chunk_index: int
    content: str
    distance: float


class ChatResponse(BaseModel):
    """响应体结构"""
    reply: str
    session_id: int
    user_message_id: int
    assistant_message_id: int
    latency_ms: int
    sources: list[ChatSource]


class ChatSessionResponse(BaseModel):
    """响应会话"""
    id: int
    title: str
    created_at: datetime


class ChatMessageResponse(BaseModel):
    """响应会话消息"""
    id: int
    session_id: int
    role: str
    content: str
    created_at: datetime
