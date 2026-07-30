import sys
from pathlib import Path

# Đưa thư mục codebase vào sys.path để import các module dễ dàng
current_dir = Path(__file__).resolve().parent
codebase_dir = current_dir.parent
sys.path.insert(0, str(codebase_dir))

from env_loader import get_config
from providers.openai_provider import OpenAIProvider

def run_preflight_check():
    print("="*60)
    print("🚀 PREFLIGHT CHECK - KIỂM TRA KẾT NỐI OPENAI PROVIDER")
    print("="*60)
    
    config = get_config()
    api_key = config.get("OPENAI_API_KEY", "")
    model = config.get("DEFAULT_MODEL", "gpt-4o-mini")
    
    if not api_key:
        print("[FAILED] ❌ KHÔNG TẤY OPENAI_API_KEY trong file .env!")
        print("Vui lòng mở file codebase/.env và kiểm tra lại API key của bạn.")
        sys.exit(1)
        
    print(f"[INFO] 🔑 Đã tìm thấy OpenAI API Key: {api_key[:8]}...{api_key[-4:]}")
    print(f"[INFO] 🤖 Đang kiểm tra model nhẹ theo cấu hình: {model}")
    
    try:
        provider = OpenAIProvider(api_key=api_key, model_name=model)
        test_prompt = "Say 'Hello from PhishShield AI!' in JSON format with key 'message'."
        print("[INFO] 🌐 Đang gọi OpenAI API (JSON mode)...")
        
        result = provider.generate_json(
            prompt=test_prompt,
            system_prompt="You are a warm, professional AI assistant."
        )
        print(f"[SUCCESS] ✅ API phản hồi JSON hợp lệ:\n{result}")
        print("="*60)
        print("🎉 TRÌNH TRẠNG: MÔI TRƯỜNG & LLM PROVIDER HOẠT ĐỘNG HOÀN HẠO!")
        print("="*60)
    except Exception as e:
        print(f"[FAILED] ❌ Lỗi khi thực hiện cuộc gọi API test: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_preflight_check()
