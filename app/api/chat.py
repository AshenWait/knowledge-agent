from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.chat import (
    ChatMessageResponse,
    ChatRequest,
    ChatResponse,
    ChatSessionResponse,
)
from app.services.chat import ChatService

#前台接待员”：收请求、校验格式、调用 service

"""
prefix="/api"
设置路径前缀
这个路由器下的所有路由都会自动添加 /api前缀
比如：如果定义了路由 /messages，实际访问路径是 /api/messages
"""
router = APIRouter(prefix="/api", tags=["chat"])

#ChatRequest 是Pydantic 定义请求体结构，限制客户端必须传哪些字段，以及这些字段的类型。
#response_model 会告诉 FastAPI：这个接口应该返回什么结构；FastAPI 会据此生成文档、过滤多余字段，并在返回结构错误时抛出响应校验错误。
@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    """获取请求体，验证参数，调用LLM返回结果 

    Args:
        request (ChatRequest): 请求体
        db (Session, optional): 我需要一个数据库会话，类型是 Session. Defaults to Depends(get_db).

    Returns:
        ChatResponse: _description_
    """

    service = ChatService(db)#创建业务对象
    #根据 id获取文档
    if request.document_id is not None:
        document = service.document_service.get_document(request.document_id)
        if document is None:
            raise HTTPException(status_code=404, detail="文档不存在")
    #是否选定某会话
    if request.session_id is None:
        title = service.build_session_title(request.message)
        chat_session = service.create_session(title)#创建一条聊天会话
    else:
        chat_session = service.get_session(request.session_id)
        if chat_session is None:
            raise HTTPException(status_code=404, detail="聊天会话不存在")
    answer, latency, sources = service.chat(
        request.message,
        request.document_id,
        session_id=chat_session.id,
    )#调用 LLM 得到回答、耗时、切片数据
    user_message = service.add_message(chat_session.id,"user", request.message)#保存用户消息
    assistant_message = service.add_message(chat_session.id, "assistant", answer)#保存模型回答

    return ChatResponse(
        reply=assistant_message.content,
        session_id=chat_session.id,
        user_message_id=user_message.id,
        assistant_message_id=assistant_message.id,
        latency_ms=int(latency * 1000),
        sources=sources,
    )

@router.get("/chat/sessions", response_model=list[ChatSessionResponse])
def list_chat_sessions(db: Session = Depends(get_db)) -> list:
    service = ChatService(db)
    return service.list_sessions()

@router.get("/chat/sessions/{session_id}/messages", response_model=list[ChatMessageResponse])
def list_chat_messages(session_id: int, db: Session = Depends(get_db)) -> list:
    service = ChatService(db)
    chat_session = service.get_session(session_id)
    if chat_session is None:
        raise HTTPException(status_code=404, detail="聊天会话不存在")

    return service.list_messages(session_id)

@router.delete("/chat/sessions/{session_id}")
def delete_chat_session(session_id: int, db: Session = Depends(get_db)) -> dict[str, int | str]:
    service = ChatService(db)
    deleted = service.delete_session(session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="聊天会话不存在")

    return {
        "session_id": session_id,
        "message": "聊天会话已删除",
    }
