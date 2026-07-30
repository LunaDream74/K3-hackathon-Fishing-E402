from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class LLMProvider(ABC):
    """
    Interface cơ sở cho mọi LLM Provider trong hệ thống PhishShield AI.
    Giúp dễ dàng chuyển đổi giữa OpenAI, Gemini hay các model mã nguồn mở.
    """
    
    def __init__(self, model_name: str):
        self.model_name = model_name

    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.1) -> str:
        """
        Gọi LLM và trả về chuỗi văn bản thuần (text).
        Temperature mặc định 0.1 để đảm bảo tính nhất quán (deterministic) trong phân tích an ninh.
        """
        pass

    @abstractmethod
    def generate_json(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.1) -> Dict[str, Any]:
        """
        Gọi LLM và bắt buộc trả về định dạng từ điển JSON đã được parse.
        Tối ưu cho việc giao tiếp với Frontend UI và Benchmark Evaluation.
        """
        pass
