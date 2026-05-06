from sqlalchemy.orm import Session

from app.services.document import DocumentService
from app.services.embedding import EmbeddingService
from app.services.llm import LLMService


def retrieve_documents(db: Session, query: str, limit: int = 3) -> list[dict]:
    """根据用户问题检索相关文档片段，作为 Agent 的只读工具。"""
    embedding_service = EmbeddingService()
    query_embedding = embedding_service.embed_text(query)

    document_service = DocumentService(db)
    results = document_service.search_similar_chunks(
        query_embedding,
        limit=limit,
    )

    return [
        {
            "chunk_id": chunk.id,
            "document_id": chunk.document_id,
            "page_number": chunk.page_number,
            "chunk_index": chunk.chunk_index,
            "content": chunk.content,
            "distance": distance,
        }
        for chunk, distance in results
    ]


def summarize_document(
    db: Session,
    document_id: int,
    max_chunks: int = 8,
) -> dict:
    """总结指定文档，并返回用于生成总结的引用来源。"""
    document_service = DocumentService(db)
    document = document_service.get_document(document_id)

    if document is None:
        raise ValueError("文档不存在")

    chunks = document_service.list_chunks(document_id)
    selected_chunks = chunks[:max_chunks]

    if not selected_chunks:
        raise ValueError("文档没有可总结的内容")

    context = "\n\n".join(
        f"引用 {index + 1}，第 {chunk.page_number} 页：\n{chunk.content}"
        for index, chunk in enumerate(selected_chunks)
    )

    prompt = f"""
你是 Knowledge Agent，请根据下面的文档内容生成总结。

要求：
1. 用中文总结。
2. 先给出 3-5 条要点。
3. 最后给一句整体概括。
4. 不要编造文档里没有的信息。
5. 如果引用具体信息，请使用“引用 1”“引用 2”这样的编号。

文档名：
{document.filename}

文档内容：
{context}
"""

    llm = LLMService()
    summary, latency = llm.chat(prompt)

    sources = [
        {
            "chunk_id": chunk.id,
            "document_id": chunk.document_id,
            "document_filename": document.filename,
            "page_number": chunk.page_number,
            "chunk_index": chunk.chunk_index,
            "content": chunk.content,
        }
        for chunk in selected_chunks
    ]

    return {
        "document_id": document.id,
        "document_filename": document.filename,
        "summary": summary,
        "latency_ms": int(latency * 1000),
        "sources": sources,
    }
