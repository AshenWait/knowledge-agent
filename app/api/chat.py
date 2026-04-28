from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat import ChatService

"""
prefix="/api"
设置路径前缀
这个路由器下的所有路由都会自动添加 /api前缀
比如：如果定义了路由 /messages，实际访问路径是 /api/messages
"""
router = APIRouter(prefix="/api", tags=["chat"])

#ChatRequest 是Pydantic 定义请求体结构，限制客户端必须传哪些字段，以及这些字段的类型。
#response_model 是声明接口响应结构，FastAPI 会用它校验、过滤并生成接口文档。
#response_model 会告诉 FastAPI：这个接口应该返回什么结构；FastAPI 会据此生成文档、过滤多余字段，并在返回结构错误时抛出响应校验错误。
@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    service = ChatService(db)
    chat_session = service.create_session("Chat from API")
    
    answer, latency = service.chat(request.message)

    user_message = service.add_message(chat_session.id,"user", request.message)
    assistant_message = service.add_message(chat_session.id, "assistant", answer)

    return ChatResponse(
        reply=assistant_message.content,
        session_id=chat_session.id,
        user_message_id=user_message.id,
        assistant_message_id=assistant_message.id,
    )
