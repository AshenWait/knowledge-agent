import time
from openai import OpenAI
from app.core.config import settings

class LLMService:
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.deepseek_api_key,
            base_url="https://api.deepseek.com"

        )
    def chat(self, prompt: str, model: str = "deepseek-v4-pro") -> tuple[str, float]:
        start_time = time.time()
        response  = self.client.chat.completions.create(
            model=model,
            messages=[{"role":"user","content":prompt}]

        )
        end_time = time.time()
        latency = end_time-start_time
        answer = response.choices[0].message.content
        return answer, latency