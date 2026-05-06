from pydantic import BaseModel

from app.schemas.chat import ChatSource


class AgentChatRequest(BaseModel):
    """Agent 聊天请求体，包含用户消息和可选文档范围。"""

    message: str
    document_id: int | None = None


class AgentChatResponse(BaseModel):
    """Agent 聊天响应体，展示回答、工具调用和引用来源。"""

    reply: str
    latency_ms: int
    tool_called: str
    tool_input: str | None = None
    sources: list[ChatSource]
