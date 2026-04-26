from fastapi import APIRouter

from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/api", tags=["chat"])

#ChatRequest是Pydantic 定义请求体结构，限制客户端必须传哪些字段，以及这些字段的类型。
#response_model 是声明接口响应结构，FastAPI 会用它校验、过滤并生成接口文档。
#response_model 会告诉 FastAPI：这个接口应该返回什么结构；FastAPI 会据此生成文档、过滤多余字段，并在返回结构错误时抛出响应校验错误。
@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    return ChatResponse(reply=f"Chat endpoint received: {request.message}")
