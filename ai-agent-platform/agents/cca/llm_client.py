"""Ollama LLM Client"""
import httpx


class OllamaClient:
    def __init__(self, base_url: str = "http://ollama:11434", model: str = "llama3:8b"):
        self.base_url = base_url
        self.model = model
        self.client = httpx.AsyncClient(base_url=base_url, timeout=600.0)

    async def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = await self.client.post(
            "/api/chat",
            json={
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": 0.2,
                    "num_predict": 2048,
                    "top_p": 0.9,
                },
            },
        )
        response.raise_for_status()
        result = response.json()
        return result["message"]["content"]

    async def close(self):
        await self.client.aclose()
