from sqlalchemy.orm import Session
from app.models.document import Document, Chunk

class DocumentService:
    def __init__(self, db: Session):
        self.db = db

    def create_document(self, filename: str, file_path: str) -> Document:
        """保存文档元数据到数据库"""
        doc = Document(filename=filename, file_path=file_path)
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)
        return doc

    def list_documents(self) -> list[Document]:
        """获取所有文档列表"""
        return self.db.query(Document).all()

    def get_document(self, document_id: int) -> Document | None:
        """根据 id 获取单个文档"""
        return self.db.query(Document).filter(Document.id == document_id).first()