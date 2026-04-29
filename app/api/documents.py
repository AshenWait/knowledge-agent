from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.document import DocumentService
from app.services.pdf_parser import extract_pdf_pages

router = APIRouter(prefix="/api/documents", tags=["documents"])

UPLOAD_DIR = Path("storage/uploads")
MAX_FILE_SIZE = 10 * 1024 * 1024


@router.post("/upload")
def upload_document(
    file: UploadFile,
    db: Session = Depends(get_db),  # 每次处理上传请求时，自动帮我们创建一个数据库 Session，传给 db
) -> dict[str, str | int | None]:
    # 类型检验/限制大小
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="只支持上传 PDF 文件")

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)  # 表示目录不存在就创建，存在也不报错
    content = file.file.read()  # 读取上传文件内容
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="文件不能超过 10MB")

    file_path = UPLOAD_DIR / file.filename  # 拼接路径
    file_path.write_bytes(content)  # 保存内容

    pages = extract_pdf_pages(str(file_path))  # 解析PDF，返回列表
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
