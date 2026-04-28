from pathlib import Path

from pypdf import PdfReader


def extract_pdf_pages(file_path: str) -> list[dict[str, int | str]]:
    pdf_path = Path(file_path)  # 把字符串路径变成 Path 对象

    reader = PdfReader(pdf_path)  # 打开 PDF，读取结构

    pages: list[dict[str, int | str]] = []

    for index, page in enumerate(reader.pages, start=1):  # reader.pages 是个列表，页码从 1 开始
        text = page.extract_text() or ""  # 抽取这一页文本，如果抽不到文本，就用空字符串
        pages.append(
            {
                "page_number": index,
                "text": text,
            }
        )

    return pages
