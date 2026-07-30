# Danh Sách Thành Viên & Phân Công Công Việc
## Dự Án: PhishShield AI (Pre-Click Phishing & URL Security Classifier)
**Nhóm:** PHISHSHIELD · **Zone:**  E402
---

## 👥 Danh Sách Thành Viên & Phân Công Chi Tiết

### 1. Nguyễn Hữu Hiếu
- **Mã học viên (MSSV):** `2A202601429`
- **Vai trò chính:** Xây dựng workflow bài toán, thiết kế Agent & phát triển Tool
- **Chi tiết phân công:**
  - Phân tích luồng nghiệp vụ bài toán phân loại an toàn URL tiền truy cập (Pre-click URL Protection).
  - Thiết kế kiến trúc bộ não `PhishingAgent` theo Mô hình Lai (Hybrid Architecture): Tầng 1 Rule-based Whitelist Engine & Tầng 2 OpenAI LLM Reasoning Engine.
  - Tinh chỉnh System Prompt (`system_prompt.md`) định hướng đánh giá rủi ro URL và xây dựng các helper tools (`url_scanner.py`, `_shared.py`).

---

### 2. Nguyễn Hữu Thắng
- **Mã học viên (MSSV):** `2A202601435`
- **Vai trò chính:** Xây dựng workflow bài toán, Đánh giá (Eval) & Biên soạn Spec
- **Chi tiết phân công:**
  - Biên soạn tài liệu kỹ thuật AI Spec (`spec.md`) phủ đủ 9 phần theo khung yêu cầu.
  - Thiết kế bộ dữ liệu kiểm thử chuẩn **Golden Set 25 cases** (`golden_set.json`), bảo đảm phủ đủ 4 Lớp Chỗ Khó (4 Hard Spots) và 68% dữ liệu quan sát thực tế (Survey).
  - Xây dựng và thực thi script kiểm thử tự động (`run_eval.py`), lập báo cáo đánh giá hệ thống (`REPORT.md` & `transcripts/report.md`), ghi nhận nhật ký Validation người dùng (`validation/user_test_feedback.md`).

---

### 3. Trần Nguyễn Anh Minh
- **Mã học viên (MSSV):** `2A202601475`
- **Vai trò chính:** Xây dựng workflow bài toán & Thiết kế Giao diện (UI)
- **Chi tiết phân công:**
  - Đóng góp xây dựng luồng trải nghiệm bài toán người dùng (4 đường đi trải nghiệm: Happy path, Low-confidence, Failure, Correction).
  - Thiết kế giao diện tương tác người dùng (UI / Extension Prototype), hiển thị trực quan 3 mức phân loại rủi ro (`SAFE`, `WARNING`, `DANGER`).
  - Trực quan hóa Điểm số rủi ro (Risk Score 0-100) và danh sách lý do nghi vấn kỹ thuật (`suspicious_elements`) giúp tăng tính minh bạch và độ tin cậy cho người dùng.

---

## 📊 Bảng Tóm Tắt Nhanh

| STT | Họ và Tên | Mã học viên (MSSV) | Phân công chính |
|:---:|---|:---:|---|
| **1** | **Nguyễn Hữu Hiếu** | `2A202601429` | Workflow bài toán, Thiết kế Agent & Tool |
| **2** | **Nguyễn Hữu Thắng** | `2A202601435` | Workflow bài toán, Eval & Biên soạn Spec |
| **3** | **Trần Nguyễn Anh Minh** | `2A202601475` | Workflow bài toán, Thiết kế Giao diện (UI) |
