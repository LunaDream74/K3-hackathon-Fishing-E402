# Bài Thu Hoạch Phản Tư Cá Nhân (Personal Reflection Log)
## Dự Án: PhishShield AI (Pre-Click Phishing & URL Security Classifier)
**Họ và tên:** Trần Nguyễn Anh Minh  
**Mã học viên (MSSV):** `2A202601475`  
**Vai trò chính:** Frontend & UX Lead — Workflow bài toán, Thiết kế Giao diện (UI / Extension Prototype) (`phishshield-extension.html`, `codebase/extension-host/verify-contract.js`, `codebase/bridge.py`)  
**Nhóm:** PHISHSHIELD · **Zone:** E402  

---

## 🛠️ 1. Vai Trò & Phân Công Chi Tiết (Nội Dung Sẵn Sàng Trả Lời Vibe-Coding)

Trong dự án PhishShield AI, tôi trực tiếp chịu trách nhiệm về **giao diện tương tác người dùng (User Interface & Chrome Extension Mockup)**:

1. **Thiết Kế Giao Diện Extension Prototype (`phishshield-extension.html`):**
   - Xây dựng giao diện Chrome Extension dạng popup trực quan, giúp người dùng dễ dàng kiểm tra độ an toàn của đường liên kết URL trước khi truy cập.
   - Thể hiện rõ 3 mức phân loại phân cấp theo màu sắc thị giác chuẩn bảo mật: `SAFE` (Thẻ xanh lá - An toàn), `WARNING` (Thẻ vàng - Thận trọng/Nghi vấn), và `DANGER` (Thẻ đỏ - Nguy hiểm/Chặn).

2. **Trực Quan Hóa Điểm Số Rủi Ro & Nguyên Tắc HAX/PAIR:**
   - **Thanh đo Risk Score (0-100):** Thiết kế thanh progress bar chuyển màu động theo điểm rủi ro (HAX G2 — Làm rõ hệ thống làm tốt đến đâu).
   - **Danh sách yếu tố nghi vấn kỹ thuật (`suspicious_elements`):** Hiển thị rõ các căn cứ kỹ thuật (giả mạo tên miền VLearn, IP thô, TLD rủi ro cao, Open Redirect) dạng danh sách gạch đầu dòng trực quan (HAX G11 — Giải thích vì sao).

3. **Hiện Thực Hóa 4 Đường Đi Trải Nghiệm (4 User Flow Paths):**
   - **Happy Path:** Dán link chuẩn `vlearn.vn` -> Nhận phản hồi `SAFE` tức thì (Rule Hit 0ms).
   - **Low-confidence Path:** Dán link đối tác chưa verify -> Nhận cảnh báo màu vàng `WARNING` kèm lời nhắc HAX G10.
   - **Failure Path:** Dán link lừa đảo `vlearn-secure.xyz` -> Nhận cảnh báo đỏ `DANGER` kèm lý do chi tiết.
   - **Correction Path:** Cho phép người dùng xem căn cứ và tự đưa ra quyết định tiếp tục hay hủy bỏ.

---

## 🤖 2. Sự Hỗ Trợ Từ AI & Trải Nghiệm Vibe-Coding

Tôi đã sử dụng các công cụ AI (v0.dev, Claude Code) để thiết kế UI/UX:

- **AI hỗ trợ cực tốt ở đâu:**
  - **Tạo khung UI HTML/CSS nhanh:** v0.dev và Claude Code giúp tôi tạo dựng giao diện Extension hiện đại với CSS Tailwind/Vanilla, hiệu ứng chuyển cảnh mượt mà và bóng mờ Glassmorphism ấn tượng chỉ trong thời gian ngắn.
  - **Tương thích Responsive & Color Tokens:** AI gợi ý bảng màu HSL chuẩn bảo mật (Red `#EF4444`, Amber `#F59E0B`, Green `#10B981`) giúp giao diện vô cùng chuyên nghiệp.

- **Điểm AI làm chưa tốt / Trôi hướng (Vibe-coding Pitfalls):**
  - **Nhầm lẫn khái niệm UX về Risk Score:** Khi AI sinh UI ban đầu, nó đặt tên nhãn con số là `"Security Score: 75/100"`. Điều này khiến người dùng chạy thử ở vòng Validation tưởng rằng 75/100 nghĩa là... 75% an toàn! Trong khi con số 75 ở hệ thống của chúng tôi là **Risk Score (Mức độ Rủi ro = 75%)**!
  - **Cách tôi làm chủ & điều chỉnh:** Tôi đã phát hiện ra điểm gây hiểu nhầm này, trực tiếp sửa lại nhãn hiển thị trong HTML thành `"Mức độ Rủi ro: 75/100 (WARNING - Thận trọng)"` và đổi thanh đo từ 0% (An toàn - Xanh) tăng dần đến 100% (Nguy hiểm - Đỏ).

---

## 💡 3. Bài Học Sâu Sắc Từ Ca Fail Của Nhóm (Failure Case & Lesson Learned)

**Ca Fail thực tế:** Sự cố giao diện gây hiểu nhầm điểm rủi ro Risk Score ở buổi test Validation người dùng (CP5).
- **Tình huống:** Tại CP5, khi đưa prototype cho người dùng Lê Văn Hoàng dùng thử case link rút gọn `bit.ly/3xYpQmZ`, màn hình hiện ra nhãn Vàng `WARNING` kèm con số `75/100`. Hoàng thắc mắc: *"Sao điểm 75/100 cao thế này mà lại bảo em cẩn thận?"*.
- **Nguyên nhân gốc rễ:** Do AI sinh giao diện theo thói quen đặt tên `"Score"`, khiến người dùng áp dụng mental model cũ (điểm càng cao = càng tốt/an toàn).
- **Cách khắc phục:** Tôi đã cập nhật lại `phishshield-extension.html` ngay trước buổi dry run: đổi tên nhãn thành `Mức độ Rủi ro (Risk Score)`, thêm tooltip giải thích và thanh progress bar đổi màu từ Xanh sang Đỏ để khớp chính xác với trực giác thị giác người dùng.
- **Bài học rút ra:** *Một giao diện AI đẹp không có nghĩa là một giao diện AI tốt. Trong sản phẩm AI, việc hiển thị thông tin (Explainability) phải hoàn toàn khớp với tâm lý người dùng (Mental Model). Nếu người dùng hiểu nhầm con số AI trả ra, hậu quả có thể dẫn đến việc họ nhấp liều vào một đường link độc hại vì tưởng nó "75% an toàn".*

---

## 🎯 4. Tự Đánh Giá & Cam Kết Vibe-Coding

Tôi hoàn toàn làm chủ cấu trúc HTML/CSS và JavaScript điều khiển UI trong `phishshield-extension.html` cũng như file giao tiếp API contract `verify-contract.js`. Tôi sẵn sàng trình diễn 4 đường đi trải nghiệm trực tiếp trên màn hình và giải thích các nguyên tắc HAX/PAIR được tích hợp trong giao diện nếu được Ban giám khảo hoặc TA yêu cầu tại CP5/CP6.
