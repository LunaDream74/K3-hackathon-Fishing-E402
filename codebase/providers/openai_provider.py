import json
from typing import Any, Dict, Optional
from openai import OpenAI, OpenAIError

from .base import LLMProvider

class OpenAIProvider(LLMProvider):
    """
    Tích hợp OpenAI API, tối ưu sử dụng model nhẹ gpt-4o-mini theo yêu cầu dự án.
    """
    def __init__(self, api_key: str, model_name: str = "gpt-4o-mini"):
        super().__init__(model_name=model_name)
        if not api_key:
            raise ValueError("[ERROR] OpenAI API Key chưa được cấu hình. Vui lòng kiểm tra file .env!")
        self.client = OpenAI(api_key=api_key)

    def _build_messages(self, prompt: str, system_prompt: Optional[str] = None):
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return messages

    def generate(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.1) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=self._build_messages(prompt, system_prompt),
                temperature=temperature
            )
            return response.choices[0].message.content.strip()
        except OpenAIError as e:
            print(f"[OpenAIProvider Error] Lỗi khi gọi OpenAI API: {e}")
            raise e

    def generate_json(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.1) -> Dict[str, Any]:
        """
        Sử dụng chế độ JSON Object chính thức của OpenAI (response_format={"type": "json_object"})
        để đảm bảo 100% kết quả trả về là JSON chuẩn hóa.
        """
        # Lưu ý của OpenAI: Trong prompt hoặc system prompt BẮT BUỘC phải có chuỗi "JSON"
        enhanced_system_prompt = (system_prompt or "") + "\n\nIMPORTANT: You must respond in valid JSON format."
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=self._build_messages(prompt, enhanced_system_prompt),
                temperature=temperature,
                response_format={"type": "json_object"}
            )
            raw_content = response.choices[0].message.content.strip()
            return json.loads(raw_content)
        except json.JSONDecodeError as jde:
            print(f"[OpenAIProvider Error] Không thể parse JSON từ kết quả trả về: {raw_content}")
            return {"error": "JSONDecodeError", "raw_content": raw_content}
        except OpenAIError as e:
            print(f"[OpenAIProvider Error] Lỗi khi gọi OpenAI API trong chế độ JSON: {e}")
            raise e
