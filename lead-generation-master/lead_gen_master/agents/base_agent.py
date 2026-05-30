from typing import Optional
from lead_gen_master.memory.memory_manager import MemoryManager


class BaseAgent:
    def __init__(self, memory: Optional[MemoryManager] = None):
        self.memory = memory or MemoryManager()
        self.name = self.__class__.__name__

    def log(self, message: str):
        print(f"[{self.name}] {message}")
