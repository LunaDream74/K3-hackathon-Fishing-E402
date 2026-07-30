import json
import sys
from pathlib import Path
from typing import Dict, Any

# Hỗ trợ import nội bộ khi chạy độc lập hoặc từ app/script khác
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from env_loader import get_config
from providers.openai_provider import OpenAIProvider
from tools import scan_text_and_urls

class PhishingAgent:
    """
    Bộ não trung tâm của hệ thống PhishShield AI (Phase 1: URL Focus).
    Triển khai mô hình lai (Hybrid Architecture):
    - Tầng 1: Quy tắc tĩnh (Rule-based / Whitelist Engine) -> Giải quyết 80% link rõ rệt (Nhanh nhạy, Miễn phí).
    - Tầng 2: LLM Reasoning (OpenAI gpt-4o-mini) -> Giải quyết các ca lạ, tinh vi, cần diễn giải ngữ cảnh.
    """
    def __init__(self, model_name: str = "gpt-4o-mini"):
        config = get_config()
        api_key = config.get("OPENAI_API_KEY", "")
        if not api_key:
            raise ValueError("[PhishingAgent Error] Không tìm thấy OPENAI_API_KEY trong file .env!")
            
        self.provider = OpenAIProvider(api_key=api_key, model_name=model_name)
        self.system_prompt = self._load_system_prompt()
        
    def _load_system_prompt(self) -> str:
        prompt_path = current_dir / "artifacts" / "system_prompt.md"
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"[Warning] Không thể tải system_prompt.md: {e}. Sử dụng prompt mặc định.")
            return "You are a Cybersecurity AI Agent helping employees identify phishing emails and malicious URLs. Respond in JSON format with keys: risk_level, risk_score, suspicious_elements, recommendation."

    def analyze_email(self, text_input: str) -> Dict[str, Any]:
        """
        Hàm thực thi phân tích chính, trả về JSON dictionary kết quả.
        """
        print(f"\n[Agent] 🔍 Đang phân tích nội dung đầu vào ({len(text_input)} ký tự)...")
        
        # Bước 1: Cho đi qua Bộ lọc tĩnh URL Scanner (Tool Layer)
        scan_result = scan_text_and_urls(text_input)
        extracted_urls = scan_result.get("extracted_urls", [])
        print(f"[Agent] 🌐 Phát hiện {len(extracted_urls)} đường link: {extracted_urls}")
        
        # Bước 2: Kiểm tra xem có thể trả về kết quả bằng Rule-based mà không cần tốn tiền gọi LLM không
        if not scan_result.get("needs_llm_call", True):
            print("[Agent] ⚡ Quy tắc an toàn/độc hại đã rõ ràng! Bỏ qua gọi LLM (Tiết kiệm Token & Latency).")
            res = scan_result["deterministic_result"]
            res["extracted_urls"] = extracted_urls
            return res
            
        # Bước 3: Ca kiểm thử nghi vấn hoặc mơ hồ -> Kế tiếp gọi OpenAI gpt-4o-mini (Reasoning Engine)
        print(f"[Agent] 🤖 Phát hiện liên kết cần thẩm định sâu -> Đang gửi yêu cầu phân tích tới OpenAI ({self.provider.model_name})...")
        
        url_context_json = json.dumps(scan_result.get("url_analyses", []), ensure_ascii=False)
        user_prompt = (
            f"NỘI DUNG EMAIL / VĂN BẢN CẦN PHÂN TÍCH:\n\"\"\"{text_input}\"\"\"\n\n"
            f"BÁO CÁO TRÍCH XUẤT URL SƠ BỘ TỪ CÔNG CỤ KỸ THUẬT:\n{url_context_json}\n\n"
            "Hãy đánh giá rủi ro và trả về chuẩn JSON object theo quy trình trong System Prompt."
        )
        
        llm_response = self.provider.generate_json(
            prompt=user_prompt,
            system_prompt=self.system_prompt
        )
        
        llm_response["extracted_urls"] = extracted_urls
        llm_response["analysis_source"] = f"LLM_REASONING ({self.provider.model_name})"
        return llm_response

# -----------------------------------------------------------------------------
# KIỂM THỬ NHANH NGAY TẠI MODULE AGENT (DEMO VERIFICATION)
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    print("="*70)
    print("🛡️ KIỂM THỬ BỘ NÃO PHISHSHIELD AI AGENT (PHASE 1 - URL FOCUS)")
    print("="*70)
    
    try:
        agent = PhishingAgent(model_name="gpt-4o-mini")
    except Exception as err:
        print(err)
        sys.exit(1)
        
    test_cases = [
        {
            "name": "Ca 1: Link chính thức an toàn trong Whitelist (Sẽ KHÔNG gọi LLM)",
            "content": "Chào lớp, tài liệu bài học ngày hôm nay đã được cập nhật trên portal VLearn chính thức. Mọi người xem tại link: https://vlearn.vn/lesson-04"
        },
        {
            "name": "Ca 2: Link chứa địa chỉ IP tĩnh nguy hiểm rõ ràng (Sẽ KHÔNG gọi LLM)",
            "content": "Cảnh báo bảo mật: Hệ thống ghi nhận đăng nhập lạ. Vui lòng bấm vào http://45.112.33.199/login-secure để đặt lại mật khẩu ngay lập tức."
        },
        {
            "name": "Ca 3: Tên miền tinh vi giả mạo VLearn/VinAI (Sẽ GỌI OpenAI gpt-4o-mini phân tích)",
            "content": "[Bộ phận IT - VinAI] Thông báo: Mật khẩu email của bạn sẽ hết hạn sau 24 giờ tới. Xin hãy truy cập trang hỗ trợ kỹ thuật và xác thực thông tin tại https://vinai-verify-account.tk/reset-password hoặc https://vlearn-support-portal.xyz/login trước khi bị khóa."
        }
    ]
    
    for tc in test_cases:
        print("\n\n" + "#"*70)
        print(f"📌 ĐANG CHẠY: {tc['name']}")
        print(f"📩 Nội dung: \"{tc['content']}\"")
        print("#"*70)
        
        result = agent.analyze_email(tc["content"])
        print("\n📊 KẾT QUẢ PHÂN TÍCH:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
    print("\n\n🎉 HOÀN TẤT CHẠY KIỂM THỬ TOÀN BỘ BỘ NÃO AGENT!")
