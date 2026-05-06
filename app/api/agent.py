from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.schemas.agent import AgentChatRequest, AgentChatResponse
from app.services.agent import AgentService


router = APIRouter(prefix="/api/agent", tags=["agent"])


@router.post("/chat", response_model=AgentChatResponse)
def agent_chat(
    request: AgentChatRequest,
    db: Session = Depends(get_db),
) -> AgentChatResponse:
    """Agent 聊天入口：先让模型选择工具，再按需要执行工具并回答。"""
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="消息不能为空")
    if len(request.message) > settings.max_chat_message_length:
        raise HTTPException(
            status_code=400,
            detail=f"消息不能超过 {settings.max_chat_message_length} 字",
        )

    service = AgentService(db)
    if request.document_id is not None:
        document = service.tools.document_service.get_document(request.document_id)
        if document is None:
            raise HTTPException(status_code=404, detail="文档不存在")

    answer, latency_ms, tool_called, tool_input, sources = service.agent_chat(
        request.message,
        document_id=request.document_id,
    )
    return AgentChatResponse(
        reply=answer,
        latency_ms=latency_ms,
        tool_called=tool_called,
        tool_input=tool_input,
        sources=sources,
    )
