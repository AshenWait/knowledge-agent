from email import message

from pydantic import BaseModel  

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str
    session_id: int
    user_message_id: int
    assistant_message_id: int