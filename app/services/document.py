from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.document import Chunk, Document


class DocumentService:
    def __init__(self, db: Session):
        self.db = db

    def create_document(
        self,
        filename: str,
        file_path: str,
        content_type: str,
        page_count: int,
    ) -> Document:
        """保存文档元数据到数据库"""
        #doc：填好的一张登记表
        doc = Document(
            filename=filename,
            file_path=file_path,
            content_type=content_type,
            page_count=page_count,
        )
        #打开的登记窗口，可以进行操作
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)
        return doc

    def create_chunks(
        self,
        document_id: int,
        chunks: list[dict[str, str | int]],
    ) -> list[Chunk]:
        """保存文档 chunks 到数据库"""
        chunk_objects = [
            Chunk(  # chunks 表模板
                document_id=document_id,
                content=str(chunk["content"]),
                page_number=int(chunk["page_number"]),
                chunk_index=int(chunk["chunk_index"]),
                embedding=chunk.get("embedding"),
                embedding_model=chunk.get("embedding_model"),
            )
            for chunk in chunks
        ]
        self.db.add_all(chunk_objects)  # 放进数据库会话
        self.db.commit()  # 真正写进 PostgreSQL
        for chunk in chunk_objects:
            self.db.refresh(chunk)
        return chunk_objects

    def search_similar_chunks(
        self,
        query_embedding: list[float],
        limit: int = 3,
        document_id: int | None = None,
    ) -> list[tuple[Chunk, float]]:
        """向量相似度搜索，返回 chunk 和距离"""
        distance = Chunk.embedding.cosine_distance(query_embedding).label("distance")
        statement = select(Chunk, distance).where(Chunk.embedding.is_not(None))

        if document_id is not None:
            statement = statement.where(Chunk.document_id == document_id)

        statement = statement.order_by(distance).limit(limit)
        rows = self.db.execute(statement).all()
        return [(chunk, float(score)) for chunk, score in rows]

    def list_documents(self) -> list[Document]:
        """获取所有文档列表"""
        return self.db.query(Document).all()

    def get_document(self, document_id: int) -> Document | None:
        """根据 id 获取单个文档"""
        return self.db.query(Document).filter(Document.id == document_id).first()

    def list_chunks(self, document_id: int) -> list[Chunk]:
        """查询某篇文档的 chunks"""
        return (
            self.db.query(Chunk)
            .filter(Chunk.document_id == document_id)
            .order_by(Chunk.chunk_index)
            .all()
        )

    def delete_document(self, document_id: int) -> bool:
        """根据 id 删除单个文档"""
        document = self.get_document(document_id)
        if document is None:
            return False
        self.db.query(Chunk).filter(Chunk.document_id == document_id).delete()
        self.db.delete(document)
        self.db.commit()
        return True
