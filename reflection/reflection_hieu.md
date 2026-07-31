# Bài Thu Hoạch Phản Tư Cá Nhân (Personal Reflection Log)
## Dự Án: PhishShield AI (Pre-Click Phishing & URL Security Classifier)
**Họ và tên:** Nguyễn Hữu Hiếu  
**Mã học viên (MSSV):** `2A202601429`  
**Vai trò chính:** Lead AI Engineer — Workflow bài toán, Thiết kế Agent & Phát triển Tool (`codebase/agent.py`, `codebase/tools/url_scanner.py`, `codebase/tools/_shared.py`, `codebase/artifacts/system_prompt.md`)  
**Nhóm:** PHISHSHIELD · **Zone:** E402  

---

## 🛠️ 1. Vai Trò & Phân Công Chi Tiết (Nội Dung Sẵn Sàng Trả Lời Vibe-Coding)

Trong dự án PhishShield AI, tôi trực tiếp chịu trách nhiệm về **linh hồn kỹ thuật của hệ thống AI**:

1. **Thiết kế Kiến trúc Lai (Hybrid 2-Tier Architecture):**
   - **Tầng 1 — Rule-based Whitelist & Blacklist Engine (0ms, 0 token cost):** Xây dựng bộ lọc tĩnh bằng Python (`_shared.py`, `url_scanner.py`) kiểm tra tức thì các tên miền Whitelist (`vlearn.vn`, `vinai.io`), các IP thô (`http://45.112.33.199`), các TLD rủi ro cao (`.xyz`, `.top`, `.tk`), và bóc tách tham số Open Redirect (`google.com/url?q=...`). Nếu trùng khớp quy tắc cứng, trả về ngay phán quyết `SAFE` hoặc `DANGER` mà không tốn chi phí gọi LLM.
   - **Tầng 2 — OpenAI LLM Reasoning Engine (`gpt-4o-mini`):** Khi gặp tên miền lạ hoặc ngữ cảnh mơ hồ (chưa nằm trong Whitelist/Blacklist), chuyển câu truy vấn sang `PhishingAgent` trong `agent.py` để phân tích sâu bằng LLM.

2. **Tinh chỉnh System Prompt (`codebase/artifacts/system_prompt.md`):**
   - Định dạng đầu ra nghiêm ngặt dưới dạng JSON Schema gồm các trường: `risk_score` (0-100), `classification` (`SAFE` / `WARNING` / `DANGER`), `action` (`allow` / `warn` / `block`), `suspicious_elements` (danh sách yếu tố nghi vấn kỹ thuật), và `explanation` (lý do bằng tiếng Việt dễ hiểu).
   - Thiết kế prompt theo tư duy HAX G10 (Thu hẹp phạm vi khi nghi ngờ) & G11 (Giải thích lý do) để ép model không bao giờ được "đoán liều" khi thiếu căn cứ.

3. **Phát triển Tool Bóc Tách URL (`url_scanner.py`):**
   - Viết logic Regex bóc tách hostname, TLD, query parameters, kiểm tra Open Redirect và phát hiện Typosquatting (giả mạo tên miền VLearn).

---

## 🤖 2. Sự Hỗ Trợ Từ AI & Trải Nghiệm Vibe-Coding

Trong suốt 1.5 ngày làm việc, tôi kết hợp sử dụng **Claude Code (Gemini 3.6 Flash / Claude 3.7)** làm bạn đồng hành pair-programming:

- **AI hỗ trợ cực tốt ở đâu:**
  - **Viết Regex bóc tách URL & Open Redirect:** Việc viết Regex bắt các chuỗi URL phức tạp (như `google.com/url?q=http://...` hoặc `bit.ly/...`) dễ gây ra bug trích xuất. AI giúp tôi viết các biểu thức chính quy chuẩn xác chỉ trong vài giây kèm theo unit test mẫu.
  - **Structured Output Parsing:** AI gợi ý cách dùng Pydantic / JSON schema để bắt `PhishingAgent` luôn trả về đúng định dạng JSON mà không bị trôi văn bản lung tung.

- **Điểm AI làm chưa tốt / Trôi hướng (Vibe-coding Pitfalls):**
  - Ban đầu khi được nhờ viết code phân loại URL, AI có xu hướng muốn đưa **toàn bộ 100% URL qua OpenAI API** để phán đoán. Điều này dẫn đến thời gian phản hồi bị chậm (1-2 giây cho mọi request) và làm tăng chi phí token không cần thiết cho các URL an toàn rõ ràng như `vlearn.vn`.
  - **Cách tôi làm chủ & điều chỉnh:** Tôi chủ động can thiệp vào kiến trúc, buộc AI tuân theo thiết kế 2 Tầng (Hybrid Model): Tầng 1 Rule Engine phải chạy trước, chỉ khi Tầng 1 không chốt được nhãn thì mới gọi Tầng 2 LLM. Điều này giúp tối ưu **Rule Hit Rate đạt 68.0%** (tiết kiệm 68% chi phí API).

---

## 💡 3. Bài Học Sâu Sắc Từ Ca Fail Của Nhóm (Failure Case & Lesson Learned)

**Ca Fail thực tế:** Ca bỏ sót lỗ hổng `rare_phish_03` trong bộ Golden Set ở Lượt chạy 1 & 2.
- **Tình huống:** URL `google.com/url?q=http://malicious-phishing.top` sử dụng kỹ thuật Open Redirect của Google. Trong lượt chạy đầu tiên, hệ thống Tầng 1 chỉ nhìn thấy hostname là `google.com` nên gán nhãn `SAFE` (cho qua)!
- **Nguyên nhân gốc rễ:** Logic bóc tách tên miền ban đầu chỉ lấy `urllib.parse.urlparse(url).netloc` mà quên không parse phần Query String (`?q=...`), khiến kẻ lừa đảo dễ dàng mượn uy tín tên miền Google để che giấu trang web độc hại phía sau.
- **Cách khắc phục:** Tôi đã cập nhật `url_scanner.py` để bổ sung hàm `extract_redirect_target()`, phát hiện các tham số như `q=`, `redirect=`, `url=` và bóc tách URL đích thực sự ra để phân tích.
- **Bài học rút ra:** *Trong bài toán An ninh mạng & AI Security, kẻ tấn công luôn tìm cách ẩn nấp đằng sau các dịch vụ uy tín (như Google Redirect hay Bitly). AI Agent không thể tin tưởng tuyệt đối vào nhãn bề ngoài mà phải bóc tách sâu đến tận cùng dữ liệu thực sự (Root Destination). Sự kết hợp giữa Deterministic Rules (Rule cứng bóc bóc tách) và Probabilistic AI (LLM suy luận) mới là chìa khóa tạo nên hệ thống an toàn vững chắc.*

---

## 🎯 4. Tự Đánh Giá & Cam Kết Vibe-Coding

Tôi tự tin giải thích 100% từng dòng code trong `codebase/agent.py`, `url_scanner.py` và `system_prompt.md`. Nếu Ban giám khảo hoặc TA hỏi bất kỳ câu hỏi nào ngẫu nhiên tại CP5/CP6 về cơ chế bóc tách Open Redirect hay cách System Prompt ép model trả đúng JSON Schema, tôi hoàn toàn chủ động giải thích mạch lạc và minh minh chứng bằng code thực tế trong repo.
