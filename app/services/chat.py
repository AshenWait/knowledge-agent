from sqlalchemy.orm import Session

from app.models.chat import ChatSession, ChatMessage
from app.services.document import DocumentService
from app.services.embedding import EmbeddingService
from app.services.llm import LLMService

class ChatService:
    def __init__(self, db:Session):
        self.db = db
        self.llm = LLMService()
        self.embedding = EmbeddingService()
        self.document_service = DocumentService(db)
    
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

    def chat(self, user_message: str) -> tuple[str, float]:
        query_embedding = self.embedding.embed_text(user_message)
        chunks = self.document_service.search_similar_chunks(query_embedding, limit=3)
        context = "\n\n".join(
            f"资料{index+1}:\n{chunk.content}"
            for index, chunk in enumerate(chunks)
        )
        prompt = f"""
你是 Knowledge Agent，请根据下面的资料回答用户问题。

如果资料里没有答案，请回答：我在已上传文档里没有找到足够信息。

资料：
{context}

用户问题：
{user_message}
"""

        answer, latency = self.llm.chat(prompt)    
        return answer, latency
