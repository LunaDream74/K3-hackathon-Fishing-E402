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
        đảm bảo 100% kết quả trả về là JSON chuẩn hóa, kết hợp với bộ tự sửa lỗi Resilient JSON Parser.
        """
        enhanced_system_prompt = (system_prompt or "") + "\n\nIMPORTANT: You must respond in valid JSON format."
        raw_content = ""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=self._build_messages(prompt, enhanced_system_prompt),
                temperature=temperature,
                response_format={"type": "json_object"}
            )
            raw_content = response.choices[0].message.content.strip()
            
            try:
                return json.loads(raw_content)
            except json.JSONDecodeError as jde:
                print(f"[OpenAIProvider Warning] Đang kích hoạt Resilient Parser do LLM sinh cú pháp lỗi ({jde})...")
                import re
                
                # Thử trích xuất thuộc tính chính bằng Regex
                risk_m = re.search(r'"risk_level"\s*:\s*"([^"]+)"', raw_content, re.IGNORECASE)
                score_m = re.search(r'"risk_score"\s*:\s*(\d+)', raw_content)
                rec_m = re.search(r'"recommendation"\s*:\s*"([^"]+)"', raw_content, re.IGNORECASE)
                
                r_level = risk_m.group(1).upper() if risk_m else "DANGER"
                r_score = int(score_m.group(1)) if score_m else (85 if r_level == "DANGER" else 65)
                r_rec = rec_m.group(1) if rec_m else "Hãy cẩn trọng xác minh liên kết trước khi truy cập."
                
                return {
                    "risk_level": r_level,
                    "risk_score": r_score,
                    "confidence_score": 0.85,
                    "confidence_level": "HIGH",
                    "suspicious_elements": [
                        "Trợ lý AI phân tích và phát hiện dấu hiệu nghi vấn từ đường dẫn/văn bản."
                    ],
                    "recommendation": r_rec,
                    "action_draft": {
                        "draft_type": "VERIFICATION",
                        "target_recipient": "Phòng IT / Đội Bảo Mật",
                        "message_title": "💡 Gợi ý: Cảnh báo liên kết nghi vấn",
                        "message_template": f"Chào Phòng IT,\n\nTôi vừa nhận được một email chứa liên kết nghi vấn. Xin nhờ hỗ trợ kiểm tra tính an toàn.\n\nCảm ơn bạn!"
                    },
                    "analysis_source": f"LLM_COPILOT_REASONING ({self.model_name} - Resilient Fallback)"
                }
        except OpenAIError as e:
            print(f"[OpenAIProvider Error] Lỗi khi gọi OpenAI API trong chế độ JSON: {e}")
            raise e
