from abc import ABC, abstractmethod
from typing import Optional


class LLMProvider(ABC):
    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        ...

    @abstractmethod
    def is_available(self) -> bool:
        ...

    def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
    ) -> str:
        return self.generate(
            prompt=prompt,
            system_prompt=(
                system_prompt
                or "You are a data extraction assistant. "
                "Return ONLY valid JSON without markdown formatting."
            ),
            temperature=temperature,
        )
