from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.document import DocumentResponse
from app.services.document import DocumentService
from app.services.document_parser import parse_document

router = APIRouter(prefix="/api/documents", tags=["documents"])

UPLOAD_DIR = Path("storage/uploads")
MAX_FILE_SIZE = 10 * 1024 * 1024
ALLOWED_SUFFIXES = {".pdf", ".txt", ".md", ".markdown"}


@router.post("/upload")
def upload_document(
    file: UploadFile,
    db: Session = Depends(get_db),  # 每次处理上传请求时，自动帮我们创建一个数据库 Session，传给 db
) -> dict[str, str | int | None]:
    # 类型检验/限制大小
    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise HTTPException(status_code=400, detail="只支持上传 PDF、txt、markdown 文件")

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)  # 表示目录不存在就创建，存在也不报错
    content = file.file.read()  # 读取上传文件内容

    if len(content) == 0:
        raise HTTPException(status_code=400, detail="文件不能为空")
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="文件不能超过 10MB")

    file_path = UPLOAD_DIR / file.filename  # 拼接路径
    file_path.write_bytes(content)  # 保存内容

    try:
        pages = parse_document(str(file_path), file.filename)  # 解析文档，返回统一列表
    except Exception as exc:
        raise HTTPException(status_code=400, detail="文档解析失败，请检查文件是否损坏") from exc

    has_text = any(str(page["text"]).strip() for page in pages)
    if not has_text:
        raise HTTPException(status_code=400, detail="文档没有可解析文本，可能是扫描版 PDF")

    service = DocumentService(db)
    # 为了返回给用户一个ID用来查询保存记录
    document = service.create_document(
        filename=file.filename,
        file_path=str(file_path),
        content_type=file.content_type or "",
        page_count=len(pages),
    )
    return {
        "document_id": document.id,
        "filename": file.filename,
        "content_type": file.content_type,
        "file_path": str(file_path),
        "page_count": len(pages),
    }

@router.get("", response_model=list[DocumentResponse])
def list_documents(db: Session = Depends(get_db)) -> list[dict]:
    service = DocumentService(db)
    documents = service.list_documents()

    return [
        {
            "id": doc.id,
            "filename": doc.filename,
            "file_path": doc.file_path,
            "content_type": doc.content_type,
            "page_count": doc.page_count,
            "created_at": doc.created_at,
        }
        for doc in documents
    ]


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(document_id: int, db: Session = Depends(get_db)) -> dict:
    service = DocumentService(db)
    document = service.get_document(document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="文档不存在")

    return {
        "id": document.id,
        "filename": document.filename,
        "file_path": document.file_path,
        "content_type": document.content_type,
        "page_count": document.page_count,
        "created_at": document.created_at,
    }


@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
) -> dict[str, int | str]:
    service = DocumentService(db)
    deleted = service.delete_document(document_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="文档不存在")
    return {
        "document_id": document_id,
        "message": "文档已删除",
    }
