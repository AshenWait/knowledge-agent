from sqlalchemy.orm import Session

from app.models.document import Document


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

    def list_documents(self) -> list[Document]:
        """获取所有文档列表"""
        return self.db.query(Document).all()

    def get_document(self, document_id: int) -> Document | None:
        """根据 id 获取单个文档"""
        return self.db.query(Document).filter(Document.id == document_id).first()

    def delete_document(self, document_id: int) -> bool:
        """根据 id 删除单个文档"""
        document = self.get_document(document_id)
        if document is None:
            return False
        self.db.delete(document)
        self.db.commit()
        return True
