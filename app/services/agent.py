import re
from typing import Any

from sqlalchemy.orm import Session

from app.services.tools import (
    list_documents,
    retrieve_documents,
    summarize_document,
)


class AgentService:
    """最小 Agent 主循环：判断工具、执行工具、返回回答。"""

    def __init__(self, db: Session, max_tool_calls: int = 5):
        self.db = db
        self.max_tool_calls = max_tool_calls

    def run(self, user_message: str) -> dict[str, Any]:
        tool_calls = []
        current_message = user_message.strip()

        if not current_message:
            return {
                "answer": "问题不能为空。",
                "tool_calls": tool_calls,
            }

        for _ in range(self.max_tool_calls):
            tool_name, tool_input = self._decide_tool(current_message)

            if tool_name == "none":
                return {
                    "answer": "这个问题暂时不需要调用工具。",
                    "tool_calls": tool_calls,
                }

            try:
                tool_result = self._run_tool(tool_name, tool_input)
            except Exception as exc:
                return {
                    "answer": f"工具调用失败：{exc}",
                    "tool_calls": tool_calls,
                }

            tool_calls.append(
                {
                    "tool_name": tool_name,
                    "tool_input": tool_input,
                    "tool_result": tool_result,
                    "status": "success",
                }
            )

            return {
                "answer": self._build_answer(tool_name, tool_result),
                "tool_calls": tool_calls,
            }

        return {
            "answer": f"工具调用次数超过限制：{self.max_tool_calls}",
            "tool_calls": tool_calls,
        }

    def _decide_tool(self, user_message: str) -> tuple[str, dict[str, Any]]:
        if "哪些文档" in user_message or "文档列表" in user_message:
            return "list_documents", {}

        if "总结" in user_message and "文档" in user_message:
            document_id = self._extract_first_number(user_message)
            if document_id is None:
                return "summarize_document", {"document_id": None}
            return "summarize_document", {"document_id": document_id}

        if "文档" in user_message or "资料" in user_message or "知识库" in user_message:
            return "retrieve_documents", {"query": user_message, "limit": 3}

        return "none", {}

    def _run_tool(self, tool_name: str, tool_input: dict[str, Any]) -> Any:
        if tool_name == "list_documents":
            return list_documents(self.db)

        if tool_name == "retrieve_documents":
            return retrieve_documents(
                self.db,
                query=tool_input["query"],
                limit=tool_input.get("limit", 3),
            )

        if tool_name == "summarize_document":
            document_id = tool_input.get("document_id")
            if document_id is None:
                raise ValueError("请提供要总结的文档 id")
            return summarize_document(self.db, document_id=document_id)

        raise ValueError(f"未知工具：{tool_name}")

    def _build_answer(self, tool_name: str, tool_result: Any) -> str:
        if tool_name == "list_documents":
            if not tool_result:
                return "你还没有上传任何文档。"

            lines = ["你已经上传了这些文档："]
            for document in tool_result:
                lines.append(
                    f'- #{document["document_id"]} {document["filename"]}，'
                    f'{document["page_count"]} 页'
                )
            return "\n".join(lines)

        if tool_name == "retrieve_documents":
            if not tool_result:
                return "我在知识库里没有检索到相关片段。"

            lines = ["我检索到了这些相关片段："]
            for item in tool_result:
                lines.append(
                    f'- chunk #{item["chunk_id"]}，第 {item["page_number"]} 页，'
                    f'distance={item["distance"]:.4f}'
                )
            return "\n".join(lines)

        if tool_name == "summarize_document":
            return str(tool_result["summary"])

        return str(tool_result)

    def _extract_first_number(self, text: str) -> int | None:
        match = re.search(r"\d+", text)
        if match is None:
            return None
        return int(match.group())
