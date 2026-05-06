from sqlalchemy.orm import Session

from app.core.config import settings
from app.services.document import DocumentService
from app.services.embedding import EmbeddingService


class AgentToolService:
    """Agent 可调用的工具集合。"""

    def __init__(self, db: Session):
        """初始化工具服务，准备好 embedding 和文档查询能力。"""
        self.document_service = DocumentService(db)
        self.embedding = EmbeddingService()

    def retrieve_documents(
        self,
        query: str,
        document_id: int | None = None,
        limit: int | None = None,
    ) -> list[dict[str, int | str | float]]:
        """根据问题检索相关文档片段，作为 Agent 的第一个只读工具。"""
        query_embedding = self.embedding.embed_text(query)
        chunk_results = self.document_service.search_similar_chunks(
            query_embedding,
            limit=limit or settings.rag_top_k,
            document_id=document_id,
        )

        sources = []
        for chunk, distance in chunk_results:
            if distance > settings.max_rag_distance:
                continue

            document = self.document_service.get_document(chunk.document_id)
            sources.append(
                {
                    "chunk_id": chunk.id,
                    "document_id": chunk.document_id,
                    "document_filename": document.filename if document else "",
                    "page_number": chunk.page_number,
                    "chunk_index": chunk.chunk_index,
                    "content": chunk.content,
                    "distance": distance,
                }
            )

        return sources
