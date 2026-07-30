import os
from pathlib import Path
from dotenv import load_dotenv

def load_environment():
    """
    Load biến môi trường từ file .env trong thư mục codebase hoặc thư mục gốc.
    Ưu tiên tìm file .env tại codebase/.env trước.
    """
    current_dir = Path(__file__).resolve().parent
    env_path = current_dir / ".env"
    
    if not env_path.exists():
        # Thử tìm ở thư mục cha (thư mục gốc dự án)
        env_path = current_dir.parent / ".env"
        
    if env_path.exists():
        load_dotenv(dotenv_path=env_path, override=True)
    else:
        # Nếu không có file .env thì thử load từ environment systems (trong trường hợp chạy Docker/Kaggle/Deploy)
        load_dotenv()

def get_config():
    """
    Trả về dictionary cấu hình hệ thống với giá trị mặc định tối ưu cho OpenAI gpt-4o-mini (nhanh, nhẹ, rẻ).
    """
    load_environment()
    return {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY", ""),
        "DEFAULT_PROVIDER": os.getenv("DEFAULT_PROVIDER", "openai"),
        "DEFAULT_MODEL": os.getenv("DEFAULT_MODEL", "gpt-4o-mini"),
        "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO")
    }
