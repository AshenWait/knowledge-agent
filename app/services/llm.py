import time
from openai import OpenAI
from app.core.config import settings

class LLMService:
    """LLM 服务，负责调用大模型生成普通回答或流式回答。"""

    def __init__(self):
        """初始化兼容 OpenAI 协议的 DeepSeek 客户端。"""
        self.client = OpenAI(
            api_key=settings.deepseek_api_key,
            base_url="https://api.deepseek.com"

        )

    def chat(self, prompt: str, model: str = "deepseek-v4-pro") -> tuple[str, float]:
        """一次性调用大模型，返回完整回答和调用耗时。"""
        start_time = time.time()
        response  = self.client.chat.completions.create(
            model=model,
            messages=[{"role":"user","content":prompt}]

        )
        end_time = time.time()
        latency = end_time-start_time
        answer = response.choices[0].message.content
        return answer, latency

    def stream_chat(self, prompt: str, model: str = "deepseek-v4-pro"):
        """流式调用大模型，每次 yield 一小段回答文本。"""
        response = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            stream=True,
        )

        for chunk in response:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta
