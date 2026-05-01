from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse
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
    #先去数据库用这个ID获取内容，为空则返回404
    if request.document_id is not None:
        document = service.document_service.get_document(request.document_id)
        if document is None:
            raise HTTPException(status_code=404, detail="文档不存在")

    chat_session = service.create_session("Chat from API")#创建一条聊天会话
    answer, latency, sources = service.chat(request.message, request.document_id)#调用 LLM 得到回答、耗时、切片数据
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
