import json
import sys
from pathlib import Path
from typing import Dict, Any

current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from env_loader import get_config
from providers.openai_provider import OpenAIProvider
from tools import scan_text_and_urls

class PhishingAgent:
    """
    Bộ não trung tâm PhishShield AI v0.4.0 (Universal Actionable Copilot & Zero-Trust Armor).
    - Tầng 1: Smart Rule Engine 2.0 (Zero-Trust SSRF & Scheme Firewall + Auto-Drafts) -> 0 Token.
    - Tầng 2: Agentic LLM Reasoning (OpenAI gpt-4o-mini + Sandboxed Tools + AI Action Drafts).
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
            return "You are an Empathetic Cybersecurity AI Copilot. Respond in JSON format with keys: risk_level, risk_score, confidence_level, confidence_score, suspicious_elements, recommendation, action_draft."

    def analyze_email(self, text_input: str) -> Dict[str, Any]:
        """
        Hàm thực thi phân tích chính, trả về chuẩn JSON dictionary kèm Mức Độ Tự Tin & Bản nháp Hành động.
        """
        print(f"\n[Agent] 🔍 Đang lắng nghe và rà soát văn bản ({len(text_input)} ký tự)...")
        
        # Bước 1: Sàng lọc qua Smart Rule Engine 2.0 & Pre-fetch Tool Injection
        scan_result = scan_text_and_urls(text_input)
        extracted_urls = scan_result.get("extracted_urls", [])
        print(f"[Agent] 🌐 Phát hiện {len(extracted_urls)} đường link: {extracted_urls}")
        
        # Bước 2: Kiểm tra quyết định tại Cổng lọc tĩnh 2.0 & Khiên Zero-Trust
        if not scan_result.get("needs_llm_call", True):
            print("[Agent] ⚡ Smart Rule Engine 2.0 (Zero-Trust Guard) giải quyết tức thì! Bỏ qua LLM (Tiết kiệm 100% Token & Latency).")
            res = scan_result["deterministic_result"]
            res["extracted_urls"] = extracted_urls
            return res
            
        # Bước 3: Gửi Hồ sơ Kỹ thuật tới OpenAI gpt-4o-mini (LLM Reasoning & Universal Auto-Drafting)
        print(f"[Agent] 🤖 Ca kiểm chứng cần chiều sâu -> Đang kích hoạt Trợ lý OpenAI ({self.provider.model_name})...")
        
        url_context_json = json.dumps(scan_result.get("url_analyses", []), ensure_ascii=False)
        soc_eng_json = json.dumps(scan_result.get("social_engineering_audit", {}), ensure_ascii=False)
        user_prompt = (
            f"NỘI DUNG VĂN BẢN / EMAIL CẦN PHÂN TÍCH:\n\"\"\"{text_input}\"\"\"\n\n"
            f"HỒ SƠ KỸ THUẬT SƠ BỘ (TECHNICAL AUDIT PACKET) TỪ CÔNG CỤ CÁCH LY BẮT TRẮNG CỦA HỆ THỐNG:\n"
            f"- Chi tiết kiểm duyệt URL: {url_context_json}\n"
            f"- Chi tiết rà soát Ngữ pháp Thao túng tâm lý: {soc_eng_json}\n\n"
            "Hãy phát huy trí tuệ của Trợ lý Cố Vấn Bảo Mật Đồng Cảm, đánh giá rủi ro toàn cục và BẮT BUỘC soạn tạo bản nháp trả về chuẩn JSON object theo quy tắc trong System Prompt."
        )
        
        llm_response = self.provider.generate_json(
            prompt=user_prompt,
            system_prompt=self.system_prompt
        )
        
        llm_response["extracted_urls"] = extracted_urls
        llm_response["analysis_source"] = f"LLM_COPILOT_REASONING ({self.provider.model_name})"
        
        if "confidence_score" not in llm_response:
            llm_response["confidence_score"] = 0.85
            llm_response["confidence_level"] = "HIGH"
            
        return llm_response

# -----------------------------------------------------------------------------
# KIỂM THỬ THỰC CHIẾN 5 CA - HỘI TỤ ĐỦ QUA RULE, TƯỜNG LỬA ZERO-TRUST & BẢN NHÁP COPILOT
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    print("="*85)
    print("🛡️ KIỂM THỬ BỘ NÃO PHISHSHIELD AI AGENT V0.4.0 (ACTIONABLE COPILOT DRAFTS & ZERO-TRUST)")
    print("="*85)
    
    try:
        agent = PhishingAgent(model_name="gpt-4o-mini")
    except Exception as err:
        print(err)
        sys.exit(1)
        
    test_cases = [
        {
            "name": "Ca 1: Link VLearn chính thức sạch (Mức Xanh -> Nháp REPLY_ACK cảm ơn xác nhận)",
            "content": "Chào lớp, tài liệu bài học ngày hôm nay đã được cập nhật trên portal VLearn chính thức: https://vlearn.vn/lesson-04"
        },
        {
            "name": "Ca 2: Nhái tên miền Levenshtein (Mức Đỏ -> Nháp INCIDENT_REPORT gửi đội IT)",
            "content": "[Cảnh báo lương] Danh sách chi trả kỳ nghỉ lễ có tại liên kết nội bộ: https://v1earn.vn/payroll"
        },
        {
            "name": "Ca 3: Tên miền mới xa lạ + Thao túng tâm lý thúc ép (LLM tự viết nháp VERIFICATION gửi HR)",
            "content": "[Phòng Nhân Sự Tập Đoàn] Kính gửi toàn thể Anh/Chị, do yêu cầu quyết toán thuế THU NHẬP CÁ NHÂN KỲ 2026 gấp, mọi người khẩn trương bấm đăng nhập vào portal quản lý tài khoản nhân sự mới tại https://hr-payroll-portal2026.cloud/verify-account trước 17:00 hôm nay. Ai không hoàn tất sẽ bị tạm tháo danh sách trả lương kỳ này."
        },
        {
            "name": "Ca 4: Link Rút gọn Bitly & Chuyển hướng ẩn (Tool cách ly + LLM suy luận Báo Cáo)",
            "content": "Chào các bạn đồng nghiệp, phòng Tài chính vừa gởi biểu mẫu quy chuẩn thưởng Tết sớm. Các bạn xem thông tin tại liên kết rút gọn này nhé: https://bit.ly/3xYz9 hoặc https://google.com/url?q=https://unknown-external-server.work/reward-list.docx"
        },
        {
            "name": "Ca 5: Kiểm nghiệm Tường lửa Zero-Trust (Chặn SSRF & Giao thức cấm + Nháp Báo Cáo SOC)",
            "content": "Kính gửi Admin Kỹ Thuật, máy chủ báo rò rỉ log. Xin vui lòng kiểm tra tải mạng tại chuỗi liên kết nội bộ http://127.0.0.1:8080/admin-delete-all và truy xuất nhật ký bảo mật qua đường dẫn file:///etc/passwd để khắc phục gấp."
        }
    ]
    
    for tc in test_cases:
        print("\n\n" + "#"*85)
        print(f"📌 ĐANG THỰC THI: {tc['name']}")
        print(f"📩 Nội dung: \"{tc['content']}\"")
        print("#"*85)
        
        result = agent.analyze_email(tc["content"])
        print("\n📊 KẾT QUẢ PHÂN TÍCH CỐ VẤN & BẢN NHÁP (ACTIONABLE COPILOT OUTPUT):")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
    print("\n\n🎉 HOÀN TẤT CHẠY KIỂM THỬ BỘ NÃO PHISHSHIELD V0.4.0 THÀNH CÔNG!")
