import json
import time

from sqlalchemy.orm import Session

from app.services.agent_tools import AgentToolService
from app.services.llm import LLMService


class AgentService:
    """轻量 Agent 服务，负责选择工具、执行工具，并生成最终回答。"""

    def __init__(self, db: Session):
        """初始化 Agent 需要的大模型和工具集合。"""
        self.llm = LLMService()
        self.tools = AgentToolService(db)

    def decide_tool(self, message: str) -> tuple[dict[str, str], float]:
        """让模型判断当前问题是否需要调用文档检索工具。"""
        prompt = f"""
你是 Knowledge Agent 的工具选择器。

你现在只有一个工具：
- retrieve_documents(query)：当用户问题需要查询已上传文档、资料、PDF、知识库内容时使用。

如果需要工具，只输出 JSON：
{{"tool": "retrieve_documents", "query": "用户真正要检索的问题"}}

如果不需要工具，只输出 JSON：
{{"tool": "none", "answer": "直接给用户的简短回答"}}

用户问题：
{message}
"""
        raw_decision, latency = self.llm.chat(prompt)
        decision = self._parse_decision(raw_decision, message)
        return decision, latency

    def agent_chat(
        self,
        message: str,
        document_id: int | None = None,
    ) -> tuple[str, int, str, str | None, list[dict[str, int | str | float]]]:
        """执行一次 Agent 对话：先判断工具，再按需要检索和回答。"""
        start_time = time.time()
        decision, _decision_latency = self.decide_tool(message)
        tool_name = decision.get("tool", "none")

        if tool_name != "retrieve_documents":
            latency_ms = int((time.time() - start_time) * 1000)
            return (
                decision.get("answer", "这个问题不需要查询文档，我可以直接回答。"),
                latency_ms,
                "none",
                None,
                [],
            )

        tool_input = decision.get("query") or message
        sources = self.tools.retrieve_documents(
            tool_input,
            document_id=document_id,
        )

        if not sources:
            latency_ms = int((time.time() - start_time) * 1000)
            return (
                "我调用了 retrieve_documents 工具，但在已上传文档里没有找到足够信息。",
                latency_ms,
                "retrieve_documents",
                tool_input,
                [],
            )

        context = "\n\n".join(
            f"资料{index + 1}:\n{source['content']}"
            for index, source in enumerate(sources)
        )
        answer_prompt = f"""
你是 Knowledge Agent。你已经调用 retrieve_documents 工具拿到了资料。

请根据资料回答用户问题；如果资料不足，请说明资料不足。

资料：
{context}

用户问题：
{message}
"""
        answer, _answer_latency = self.llm.chat(answer_prompt)
        latency_ms = int((time.time() - start_time) * 1000)
        return answer, latency_ms, "retrieve_documents", tool_input, sources

    def _parse_decision(self, raw_decision: str, message: str) -> dict[str, str]:
        """解析模型输出的 JSON；解析失败时用关键词做保底判断。"""
        cleaned = raw_decision.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            cleaned = cleaned.removeprefix("json").strip()

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            return self._fallback_decision(message)

        if data.get("tool") == "retrieve_documents":
            return {
                "tool": "retrieve_documents",
                "query": str(data.get("query") or message),
            }

        return {
            "tool": "none",
            "answer": str(data.get("answer") or "这个问题不需要查询文档。"),
        }

    def _fallback_decision(self, message: str) -> dict[str, str]:
        """模型没有输出合法 JSON 时，用简单关键词保证流程还能继续。"""
        document_keywords = ("文档", "资料", "知识库", "PDF", "引用", "上传")
        if any(keyword in message for keyword in document_keywords):
            return {"tool": "retrieve_documents", "query": message}

        return {
            "tool": "none",
            "answer": "这个问题看起来不需要查询文档，我可以直接回答。",
        }
