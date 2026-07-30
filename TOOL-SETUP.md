# HƯỚNG DẪN CÀI ĐẶT MÔI TRƯỜNG & THIẾT LẬP CÔNG CỤ (TOOL SETUP GUIDE)

> **Dự án:** PhishShield AI — Trợ lý AI Cảnh báo & Phân tích Email Phishing  
> **Dành cho:** Tất cả các thành viên trong nhóm Hackathon  

---

## 1. Yêu cầu Tiên quyết (Prerequisites)
- **Python:** Phiên bản `3.10` trở lên.
- **Git:** Đã cài đặt trên máy.
- **API Key:** Google Gemini API Key (hoặc OpenAI / OpenRouter API Key).

---

## 2. Các Bước Cài đặt Môi trường (Step-by-Step Setup)

### Bước 1: Tạo Môi trường Ảo (Virtual Environment)
Mở cửa sổ Terminal (PowerShell hoặc Command Prompt trên Windows) tại thư mục dự án:

```powershell
# Tạo venv
python -m venv venv

# Kích hoạt venv (PowerShell trên Windows)
.\venv\Scripts\Activate.ps1

# Hoặc kích hoạt trên Command Prompt (CMD)
.\venv\Scripts\activate.bat
```

### Bước 2: Cài đặt Thư viện Phụ thuộc (Dependencies)
```powershell
pip install --upgrade pip
pip install -r codebase/requirements.txt
```

---

## 3. Cấu hình Biến Môi trường (.env)

1. Tạo file `.env` từ file mẫu `.env.example`:
   ```powershell
   copy codebase\.env.example codebase\.env
   ```

2. Mở file `codebase/.env` và dán API Key của bạn vào:
   ```env
   # API Keys
   GEMINI_API_KEY=AIzaSy...your_gemini_api_key_here...
   OPENAI_API_KEY=sk-...optional_openai_key...

   # Agent Environment Configurations
   DEFAULT_PROVIDER=gemini
   DEFAULT_MODEL=gemini-2.5-flash
   LOG_LEVEL=INFO
   ```

---

## 4. Kiểm tra Thiết lập (Preflight Verification)

Chạy script kiểm tra để xác nhận các API Key và môi trường hoạt động tốt:

```powershell
python codebase/scripts/preflight_provider.py
```

Nếu màn hình hiển thị `[SUCCESS] Gemini Provider is ready!`, bạn đã hoàn thành cài đặt!

---

## 5. Khởi chạy Ứng dụng Demo

Khởi chạy ứng dụng Web Demo (Streamlit):

```powershell
python -m streamlit run codebase/app.py
```

Ứng dụng sẽ tự động mở tại địa chỉ local: `http://localhost:8501`.
