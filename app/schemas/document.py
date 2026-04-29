from datetime import datetime

from pydantic import BaseModel


#定义了接口返回的数据格式
class DocumentResponse(BaseModel):
    id: int
    filename: str
    file_path: str
    content_type: str
    page_count: int
    created_at: datetime


class ChunkResponse(BaseModel):
    id: int
    document_id: int
    content: str
    page_number: int
    chunk_index: int
    created_at: datetime
