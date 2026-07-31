# Bài Thu Hoạch Phản Tư Cá Nhân (Personal Reflection Log)
## Dự Án: PhishShield AI (Pre-Click Phishing & URL Security Classifier)
**Họ và tên:** Nguyễn Hữu Thắng  
**Mã học viên (MSSV):** `2A202601435`  
**Vai trò chính:** Product & Eval Lead — Workflow bài toán, Biên soạn Spec, Đánh giá (Eval) & Validation (`spec.md`, `eval/golden_set.json`, `eval/run_eval.py`, `validation/user_test_feedback.md`)  
**Nhóm:** PHISHSHIELD · **Zone:** E402  

---

## 🛠️ 1. Vai Trò & Phân Công Chi Tiết (Nội Dung Sẵn Sàng Trả Lời Vibe-Coding)

Trong dự án PhishShield AI, tôi trực tiếp chịu trách nhiệm về **tư duy sản phẩm, tài liệu spec và kiểm thử đo lường hệ thống**:

1. **Biên Soạn Tài Liệu Kỹ Thuật AI Spec (`spec.md`):**
   - Hoàn thiện trọn vẹn 9 phần của `spec.md` theo khung yêu cầu.
   - Làm rõ Core JTBD, Bằng chứng bằng số (Mining & Khảo sát A/B), Bảng Impact 3 ứng viên, 4 Lớp Chỗ Khó và 8 Kịch Bản Rủi Ro tuân thủ nguyên tắc HAX/PAIR (G1, G2, G10, G11).
   - Thiết lập **Quality Bar cứng** chốt từ 23:59 Ngày 1: *"Đạt khi Accuracy ≥ 90.0%, Recall ≥ 90.0%, FPR < 5.0%."*

2. **Xây Dựng Golden Set 25 Cases (`eval/golden_set.json`):**
   - Xây dựng bộ test suite chuẩn 25 mẫu dữ liệu, phủ đủ 4 Lớp Chỗ Khó (4 Hard Spots: Nguồn sự thật, Mơ hồ, Ngoài thẩm quyền, Đặc thù domain).
   - Đảm bảo **17/25 cases (68.0%)** được trích xuất trực tiếp từ các dữ liệu quan sát thực tế (Discord khóa học, chatlog VLearn, khảo sát người dùng Spotify/Office).

3. **Phát Triển Script Kiểm Thử & Chống Sai Lệch Chỉ Số (`eval/run_eval.py`):**
   - Viết framework đánh giá tự động `run_eval.py`, cho phép chạy kiểm thử offline và online live API với `gpt-4o-mini`.
   - Thiết kế ma trận chấm điểm 3 lớp (`SAFE` / `WARNING` / `DANGER`) để đo chính xác Recall, False Positive Rate (FPR), Friction Rate, và Rule Hit Rate.

4. **Thực Hiện Vòng Validation Người Dùng (`validation/user_test_feedback.md`):**
   - Trực tiếp điều phối 5 phiên test người dùng (bao gồm 3 Willing Users), ghi lại phản hồi nguyên văn và tổng hợp changelog cải tiến UI.

---

## 🤖 2. Sự Hỗ Trợ Từ AI & Trải Nghiệm Vibe-Coding

Tôi đã sử dụng các trợ lý AI để hỗ trợ trong quá trình biên soạn Spec và lập trình Eval Script:

- **AI hỗ trợ cực tốt ở đâu:**
  - **Tự động hóa báo cáo Eval:** AI giúp viết script Python xử lý ma trận nhầm lẫn (Confusion Matrix) và tự động render bảng kết quả dưới dạng Markdown đẹp mắt trong `eval/runs/latest_run.json` và `REPORT.md`.
  - **Sinh dữ liệu kiểm thử biên (Edge Cases):** AI hỗ trợ gợi ý các dạng URL biến đổi tinh vi (như typosquatting `vlearn-secure.xyz`, IP thô kèm cổng `http://45.112.33.199:8080/login`) giúp bộ Golden Set trở nên phong phú hơn.

- **Điểm AI làm chưa tốt / Trôi hướng (Vibe-coding Pitfalls):**
  - **Chấm điểm sai bản chất sản phẩm:** Ban đầu khi tôi nhờ AI viết logic chấm điểm cho script `run_eval.py`, AI tự động gộp kết quả `WARNING` vào `SAFE/allow` (chấm nhị phân Binary Class). Điều này dẫn đến một thảm họa đo lường: mỗi khi AI phán đoán đúng một email nghi vấn là `WARNING`, script lại ghi nhận đó là ca "cho qua an toàn" và trừ điểm Recall nặng nề!
  - **Cách tôi làm chủ & điều chỉnh:** Tôi đã phát hiện ra lỗi tư duy này của AI, tự mình viết lại ma trận chấm 3 lớp riêng biệt trong `run_eval.py`, phân định rõ: `DANGER` & `WARNING` đối với email lừa đảo đều được tính là bẫy thành công (TP), và nhãn `WARNING` đối với thư sạch được tính là chỉ số **Friction** thay vì báo nhầm FP.

---

## 💡 3. Bài Học Sâu Sắc Từ Ca Fail Của Nhóm (Failure Case & Lesson Learned)

**Ca Fail thực tế:** Lỗi chấm điểm Eval 2 lớp kéo chỉ số Recall sụt giảm ảo từ 92.3% xuống 61.5% tại CP3.
- **Tình huống:** Tại CP3, nhóm chạy đánh giá Lượt 1 và Lượt 2 trên live model `gpt-4o-mini`. Kết quả trả về Recall chỉ đạt **61.5%**, thấp hơn nhiều so với Quality Bar (≥ 90.0%). Nhóm từng rất hoang mang tưởng rằng prompt hoặc model AI quá kém.
- **Nguyên nhân gốc rễ:** Khi soi lại log từng case (`latest_run.json`), tôi phát hiện ra model AI thực chất đã cảnh báo màu vàng `WARNING` cho toàn bộ các case lừa đảo mơ hồ. Tuy nhiên, script eval cũ do AI sinh ra lại gộp nhãn `WARNING` thành `SAFE` (allow). Việc gán sai logic chấm điểm khiến 4 ca cảnh báo đúng bị quy thành ca cho qua an toàn (FN ảo).
- **Cách khắc phục:** Tôi đã sửa lại `run_eval.py`, đưa ra bảng chấm điểm 3 lớp chính thức (issue #5 trong Changelog). Kết quả ở Lượt chạy 3 lập tức phản ánh đúng thực tế: **Recall tăng lên 100%**, Accuracy đạt **96.0%**, chứng minh model hoạt động cực kỳ xuất sắc.
- **Bài học rút ra:** *Đừng bao giờ tin tưởng mù quáng vào con số đánh giá do script AI sinh ra mà không soi lại từng mẫu dữ liệu thô (Look at your data!). Lỗi đo lường (Eval Metric Error) nguy hiểm không kém gì lỗi code sản phẩm. Một định nghĩa "Đúng/Sai" không chuẩn xác trong Spec sẽ bóp méo toàn bộ bức tranh năng lực của AI Agent.*

---

## 🎯 4. Tự Đánh Giá & Cam Kết Vibe-Coding

Tôi nắm rõ 100% từng case trong 25 mẫu `golden_set.json`, công thức tính các chỉ số Recall, FPR, Friction, Rule Hit trong `run_eval.py`, cũng như toàn bộ lập luận trong `spec.md` và feedback log tại `user_test_feedback.md`. Tôi sẵn sàng trả lời bất kỳ câu hỏi nào từ TA hoặc Giám khảo tại CP5/CP6 về sự khác biệt giữa Chấm 2 lớp vs 3 lớp và căn cứ thiết lập Quality Bar của nhóm.
