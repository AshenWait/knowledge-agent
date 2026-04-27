from sqlalchemy.orm import Session
from app.models.chat import ChatSession, ChatMessage

class ChatService:
    def __init__(self, db:Session):
        self.db = db
    
    def create_session(self, title:str) -> ChatSession:
        """创建新的聊天会话"""
        session = ChatSession(title=title)
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def add_message(self, session_id: int, role: str, content: str) -> ChatMessage:
        """往会话里添加一条消息"""
        message = ChatMessage(session_id=session_id, role=role, content=content)
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message