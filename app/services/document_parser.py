from pathlib import Path

from app.services.pdf_parser import extract_pdf_pages


def parse_text_file(file_path: str) -> list[dict[str, int | str]]:
    path = Path(file_path)
    text = path.read_text(encoding="utf-8")

    return [
        {
            "page_number": 1,
            "text": text,
        }
    ]


def parse_document(file_path: str, filename: str) -> list[dict[str, int | str]]:
    suffix = Path(filename).suffix.lower()

    if suffix == ".pdf":
        return extract_pdf_pages(file_path)

    if suffix in {".txt", ".md", ".markdown"}:
        return parse_text_file(file_path)

    raise ValueError("不支持的文件类型")
