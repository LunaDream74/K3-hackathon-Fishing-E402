# CẤU TRÚC THƯ MỤC DỰ ÁN & HƯỚNG DẪN PHÂN CÔNG (PROJECT STRUCTURE)

> **Dự án:** PhishShield AI — Trợ lý AI Cảnh báo & Phân tích Email Phishing  
> **Sự kiện:** Mini Hackathon AI — Batch 03 (Khoá K4 AI Thực Chiến)  
> **Mục tiêu:** Kết hợp chuẩn **Quy định Nộp bài Hackathon** (`codebase/`, `eval/`, `validation/`, `reflection/`) với **Kiến trúc AI Agent Chuyên nghiệp** (Modular Providers, Tools, Knowledge Base, Evaluation Pipeline).

---

## 🌳 Sơ đồ Cấu trúc Tổng thể Thư mục (Directory Tree)

```text
Batch03-K4-AI-Product-Hackathon/
│
├── README.md                       # 📝 Thông tin nhóm (Mã HV + Tên) & Bảng phân công chi tiết
├── TONG_QUAN_DU_AN.md              # 📘 Tổng quan bài toán, kịch bản lừa đảo & thiết kế Bộ não AI
├── THU_MUC_DU_AN.md                # 🗺️ Hướng dẫn cấu trúc thư mục & quy trình làm việc (File này)
├── TOOL-SETUP.md                   # 🛠️ Hướng dẫn cài đặt môi trường (Python, venv, API keys)
├── spec.md                         # 🎯 AI Spec hoàn chỉnh (theo 03-template-ai-spec.md, chốt trước 23:59 N1)
├── demo-slides.pdf                 # 📊 Slide thuyết trình 6 trang (nộp trước CP6)
│
├── codebase/                       # 🚀 PHÂN HỆ PROTOTYPE (Mã nguồn ứng dụng & AI Agent)
│   │
│   ├── artifacts/                  # 🎨 Quản lý System Prompt & Cấu hình Agent
│   │   ├── system_prompt.md        # System prompt gốc định hình tư duy & quy tắc an toàn của Agent
│   │   ├── tools.yaml              # Schema khai báo cấu hình danh sách tools (Function Calling)
│   │   └── version_log.csv         # Lịch sử theo dõi các lượt tinh chỉnh Prompt & Agent behavior
│   │
│   ├── company_policy/             # 📚 Tri thức / Quy định (Knowledge Base & Grounding Context)
│   │   ├── company-it-policy.md    # Quy định bảo mật IT & quy trình đổi mật khẩu chuẩn của công ty
│   │   ├── domain-whitelist.json   # Danh sách domain / email hợp lệ của bộ phận Kỹ thuật & Công ty
│   │   └── phishing-patterns.md    # Cơ sở tri thức về các kịch bản lừa đảo Email phổ biến (Spear Phishing)
│   │
│   ├── providers/                  # 🔌 Abstraction Layer kết nối các LLM Models
│   │   ├── __init__.py
│   │   ├── base.py                 # Interface / Base class chung cho LLM Provider
│   │   ├── gemini_provider.py      # Tích hợp Google Gemini API (Model chính)
│   │   └── openai_provider.py      # Tích hợp OpenAI API (GPT-4o/GPT-4o-mini dự phòng)
│   │
│   ├── tools/                      # 🛠️ Hệ thống Tools / Function Calling cho Agent
│   │   ├── __init__.py
│   │   ├── _shared.py              # Hàm bổ trợ dùng chung (regex parsing, URL extractor)
│   │   ├── email_parser/           # Tool phân tích Tiêu đề, Body & Header (SPF, DKIM, Sender)
│   │   ├── url_scanner/            # Tool bóc tách & kiểm tra rủi ro liên kết (Redirect, Homograph)
│   │   ├── policy_lookup/          # Tool tra cứu Quy định IT & Whitelist Domain công ty
│   │   └── risk_scorer/            # Tool tính toán điểm rủi ro & tổng hợp khuyến nghị
│   │
│   ├── scripts/                    # ⚙️ Script hỗ trợ kiểm tra & quản trị
│   │   ├── preflight_provider.py   # Kiểm tra API Keys & kết nối các provider trước khi khởi động
│   │   └── test_tools.py           # Unit test độc lập cho từng Tool
│   │
│   ├── agent.py                    # 🤖 Khai báo lớp PhishingAgent chính (Lý luận & Tool Loop)
│   ├── app.py                      # 💻 Giao diện ứng dụng Demo (Streamlit / Web UI)
│   ├── chat.py                     # 💬 Xử lý vòng lặp tương tác giữa User và Agent
│   ├── env_loader.py               # Tải biến môi trường (.env)
│   │
│   ├── requirements.txt            # Danh sách thư viện Python phụ thuộc
│   ├── .env.example                # File mẫu khai báo các biến môi trường & API Key
│   └── .env                        # Chứa API Key cá nhân (ĐƯỢC IGNORE KHỎI GIT)
│
├── eval/                           # 📈 PHÂN HỆ ĐÁNH GIÁ (Golden Set & Benchmark Pipeline)
│   ├── golden_set.json             # 🧪 Bộ 20-30 kịch bản email kiểm thử (Phishing + Legitimate + Ambiguous)
│   ├── run_eval.py                 # ⚙️ Engine chạy đánh giá tự động trên Golden Set
│   ├── parse_runs.py               # 📊 Phân tích log kết quả benchmark & tính Precision/Recall
│   ├── REPORT.md                   # 📝 Báo cáo kết quả đánh giá qua các lượt chạy (CP3 & CP5)
│   ├── runs/                       # 📂 Lưu kết quả chi tiết từng lượt chạy Benchmark (JSON)
│   └── transcripts/                # 📝 Nhật ký chi tiết luồng hội thoại & suy luận của Agent
│
├── validation/                     # 👥 PHÂN HỆ VERIFICATION VỚI USER THẬT
│   ├── survey_data.csv             # Log khảo sát ≥20 người dùng về pain point email phishing
│   ├── user_test_feedback.md       # Phản hồi từ ≥3 người dùng thật trải nghiệm thử Prototype tại CP5
│   └── interviews/                 # Chi tiết các buổi phỏng vấn sâu người dùng
│
└── reflection/                     # ✍️ PHÂN HỆ BÀI THU HOẠCH CÁ NHÂN (Mỗi thành viên 1 file)
    ├── reflection_member1.md       # Bài thu hoạch của Thành viên 1
    ├── reflection_member2.md       # Bài thu hoạch của Thành viên 2
    └── ...
```

---

## 🎯 Chi tiết Phân công & Nhiệm vụ theo Thư mục (Role Breakdown)

### 1. Phân hệ Bộ não AI & Core Logic (`codebase/agent.py`, `providers/`, `tools/`)
- **Phụ trách:** Dev Lead / AI Brain Developer.
- **Nhiệm vụ:**
  - Thiết kế `codebase/agent.py`: Quản lý vòng lặp lý luận (Reasoning Loop), kiểm soát System Prompt từ `artifacts/system_prompt.md`.
  - Phát triển các module kết nối LLM trong `codebase/providers/`.
  - Viết các Tool phân tích email chuyên dụng trong `codebase/tools/` (Email Parser, URL Scanner, Policy Lookup).
  - Đảm bảo xử lý 4 lớp rủi ro (Nguồn sự thật, Mơ hồ, Thẩm quyền, Domain risk).

### 2. Phân hệ Tri thức & Dữ liệu Grounding (`codebase/company_policy/`)
- **Phụ trách:** AI Product Manager / Domain Specialist.
- **Nhiệm vụ:**
  - Viết quy định bảo mật IT giả lập của công ty (`company-it-policy.md`).
  - Xây dựng danh sách Whitelist domain hợp lệ (`domain-whitelist.json`).
  - Tổng hợp danh sách mẫu các kịch bản lừa đảo tinh vi phổ biến (`phishing-patterns.md`).

### 3. Phân hệ Kiểm thử & Đánh giá (`eval/`)
- **Phụ trách:** AI QA / Test Engineer.
- **Nhiệm vụ:**
  - Thu thập & gắn nhãn **Golden Set 20-30 mẫu email** (`eval/golden_set.json`).
  - Vận hành script `eval/run_eval.py` tại mốc **CP3** và **CP5**.
  - Tổng hợp báo cáo chỉ số (Accuracy, Recall, Precision, False Negatives) vào file `eval/REPORT.md`.

### 4. Phân hệ Giao diện & Trải nghiệm Demo (`codebase/app.py`, `demo-slides.pdf`)
- **Phụ trách:** Frontend / UI-UX Developer / Presenter.
- **Nhiệm vụ:**
  - Xây dựng giao diện web demo trực quan (Streamlit/Web app) tại `codebase/app.py`.
  - Hiển thị mức độ rủi ro (Xanh/Vàng/Đỏ), bảng phân tích bằng chứng và nút hành động an toàn.
  - Tạ slide thuyết trình 6 trang (`demo-slides.pdf`) chuẩn bị cho **CP6 Demo**.

### 5. Phân hệ Validation & Spec (`spec.md`, `validation/`)
- **Phụ trách:** Product Lead / User Researcher.
- **Nhiệm vụ:**
  - Đảm bảo file `spec.md` phủ đầy đủ 8 phần theo đúng template `03-template-ai-spec.md` (nộp trước 23:59 N1).
  - Khảo sát $\ge 20$ người dùng và tổ chức test thử prototype với $\ge 3$ người thật ngoài nhóm, ghi log vào `validation/user_test_feedback.md`.

---

## 🚀 Hướng dẫn Bắt đầu Nhanh cho Thành viên Nhóm

### Bước 1: Khởi tạo Môi trường Làm việc
1. Mở Terminal tại thư mục gốc của dự án.
2. Làm theo hướng dẫn chi tiết trong [TOOL-SETUP.md](file:///d:/tai%20lieu%20hoc%20tap/VinAI/Day05_06_hackathon/Lap/Batch03-K4-AI-Product-Hackathon/TOOL-SETUP.md).
3. Tạo file `.env` từ `.env.example` và điền `GEMINI_API_KEY`:
   ```bash
   cp codebase/.env.example codebase/.env
   ```

### Bước 2: Kiểm tra Kết nối API
Chạy script kiểm tra API key:
```bash
python codebase/scripts/preflight_provider.py
```

### Bước 3: Khởi chạy Giao diện Demo
```bash
python -m streamlit run codebase/app.py
```

---

## ⚠️ Quy tắc An toàn & Quy chuẩn Code (Git Rules)

1. **Bảo mật API Key & Data:**
   - **TAY KHÔNG COMMIT FILE `.env` LÊN GIT.** Đường dẫn `.env` bắt buộc phải có trong `.gitignore`.
   - Không commit dữ liệu cá nhân thật hoặc dữ liệu thuộc `data/` pack vào repo nộp bài.

2. **Quy chuẩn Code Tools (`codebase/tools/`):**
   - Mỗi Tool nằm trong 1 thư mục riêng hoặc 1 file module độc lập.
   - Luôn có docstring mô tả chi tiết tham số vào/ra để LLM hiểu và thực hiện Function Calling chuẩn xác.

3. **Nguyên tắc nộp bài theo Checkpoint (CP1 - CP6):**
   - Mọi tài liệu nộp checkpoint phải đúng đường dẫn tiêu chuẩn (`spec.md`, `codebase/`, `eval/`, `validation/`, `reflection/`).
