from sqlalchemy.orm import Session

from app.core.config import settings
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

    def chat(self, user_message: str) -> tuple[str, float, list[dict[str, int | str | float]]]:
        query_embedding = self.embedding.embed_text(user_message)   #问题转向量
        # 相似度搜索返回 [(chunk1, 0.12), (chunk2, 0.35)]，distance 越小越相关
        chunk_results = self.document_service.search_similar_chunks(
            query_embedding,
            limit=settings.rag_top_k,
        )
        #过滤不相关chunks
        relevant_results = [
            (chunk, distance)
            for chunk, distance in chunk_results
            if distance <= settings.max_rag_distance
        ]
        if not relevant_results:
            return "我在已上传文档里没有找到足够信息。", 0.0, []

        #大模型只认文本，所以要把无关字段剔除
        context = "\n\n".join(
            f"资料{index+1}:\n{chunk.content}"
            for index, (chunk, distance) in enumerate(relevant_results)
        )
        prompt = f"""
你是 Knowledge Agent，请根据下面的资料回答用户问题。

如果资料里没有答案，请回答：我在已上传文档里没有找到足够信息。

资料：
{context}

用户问题：
{user_message}
"""
        #访问大模型,回答与请求耗时
        answer, latency = self.llm.chat(prompt)
        #返回给响应体
        sources = [
            {
                "chunk_id": chunk.id,
                "document_id": chunk.document_id,
                "chunk_index": chunk.chunk_index,
                "content": chunk.content,
                "distance": distance,
            }
            for chunk, distance in relevant_results
        ]
        return answer, latency, sources
