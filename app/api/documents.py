from pathlib import Path
from fastapi import APIRouter, UploadFile,HTTPException

router = APIRouter(prefix="/api/documents", tags=["documents"])

UPLOAD_DIR = Path("storage/uploads")
MAX_FILE_SIZE = 10 * 1024 * 1024


@router.post("/upload")
def upload_document(file: UploadFile) -> dict[str, str | None]:
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400,detail="只支持上传 PDF 文件")

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)#表示目录不存在就创建，存在也不报错              

    content = file.file.read()#读取上传文件内容
    if len(content)>MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="文件不能超过 10MB")
    file_path = UPLOAD_DIR / file.filename
    file_path.write_bytes(content)
    return {
        "filename":file.filename,
        "content_type":file.content_type,
        "file_path":str(file_path),
    }
