from email import message

from pydantic import BaseModel  

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str