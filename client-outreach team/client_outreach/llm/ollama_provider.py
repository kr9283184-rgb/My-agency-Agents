from typing import Optional
import requests

from client_outreach.config import Config
from client_outreach.llm.base import LLMProvider


class OllamaProvider(LLMProvider):
    def __init__(self, model: Optional[str] = None):
        self.base_url = Config.OLLAMA_BASE_URL.rstrip("/")
        self.model = model or Config.OLLAMA_MODEL

    def is_available(self) -> bool:
        try:
            resp = requests.get(
                f"{self.base_url}/api/tags", timeout=5
            )
            return resp.status_code == 200
        except requests.RequestException:
            return False

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            resp = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=120,
            )
            resp.raise_for_status()
            return resp.json().get("response", "")
        except requests.RequestException as e:
            self.log(f"Ollama error: {e}")
            return ""

    def log(self, msg: str):
        print(f"[OllamaProvider] {msg}")
