"""Ollama LLM Client"""
import httpx


class OllamaClient:
    def __init__(self, base_url: str = "http://ollama:11434", model: str = "qwen3:8b"):
        self.base_url = base_url
        self.model = model
        self.client = httpx.AsyncClient(base_url=base_url, timeout=600.0)

    async def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
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
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"Ollama returned HTTP {e.response.status_code}: {e.response.text[:500]}") from e
        except (httpx.RequestError, KeyError, ValueError) as e:
            raise RuntimeError(f"Ollama communication failed: {e}") from e

    async def close(self):
        await self.client.aclose()
