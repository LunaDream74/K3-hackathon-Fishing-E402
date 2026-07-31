# Báo Cáo Nhật Ký Validation Người Dùng (User Test Feedback Log)
## Dự Án: PhishShield AI (Pre-Click Phishing & URL Security Classifier)
**Nhóm:** PHISHSHIELD · **Zone:** E402 · **Thời gian thực hiện:** CP5 (Sáng Ngày 2)

---

## 🎯 1. Bối Cảnh & Phương Pháp Validation

- **Mục tiêu:** Thử nghiệm mức độ hiệu quả, tính minh bạch và trải nghiệm người dùng đối với các cảnh báo an toàn URL tiền truy cập (Pre-click URL Protection) trước khi demo live.
- **Đối tượng thử nghiệm:** 5 người dùng độc lập ngoài nhóm (bao gồm đủ 3 **Willing Users** đã khai báo tại mốc CP1 + 2 người dùng bên ngoài thuộc các Zone khác).
- **Kịch bản thực hiện (10 phút/phiên):**
  1. Giao task cho người thử dán các URL nghi vấn thực tế (link giả mạo Spotify, IP thô, link rút gọn `bit.ly`, link VLearn chuẩn, link Open Redirect).
  2. Im lặng quan sát hành vi thao tác, điểm họ dừng lại đọc hoặc phân vân.
  3. Hỏi trực tiếp 3 câu hỏi định hướng theo guide §4.2:
     - *Câu 1:* "Điều gì khó hiểu hoặc khó chịu nhất khi xem kết quả cảnh báo?"
     - *Câu 2:* "Kết quả đánh giá này bạn có tin tưởng không — vì sao?"
     - *Câu 3:* "Bạn có sẵn sàng cài đặt và dùng tool này hàng ngày không — vì sao / vì sao chưa?"
  4. Ghi lại phản hồi nguyên văn và đánh giá mức độ nghiêm trọng của vấn đề.

---

## 📝 2. Nhật Ký Phản Hồi Chi Tiết (Feedback Log)

| STT | Người thử (Tên/Vai) | Willing User? | Task thực hiện | Quan sát hành vi | Quote nguyên văn phản hồi | Mức độ nghiêm trọng |
|:---:|---|:---:|---|---|---|:---:|
| **1** | **Lê Văn Tuệ**<br>*(Khảo sát Spotify)* | **Có**<br>*(CP1)* | Dán URL `spotify-support.xyz` từ email thúc ép gia hạn tài khoản Spotify khẩn cấp. | Dán link vào ô kiểm tra -> Hệ thống xử lý 350ms -> Hiện khung đỏ `DANGER` (Risk Score 95/100). Tuệ đọc kỹ phần lý do tên miền rủi ro `.xyz`. | *"Ấn tượng ghê! Nút cảnh báo đỏ chót với hiện lý do đuôi `.xyz` rủi ro làm em giật mình ngay. Hồi trước em tưởng `spotify-support.xyz` là web hỗ trợ thật, giờ nhìn giải thích mới hiểu vì sao nó lừa được em."* | **Thấp** *(Feature hoạt động tốt đúng kỳ vọng)* |
| **2** | **Nguyễn Văn Phong**<br>*(Nhân viên văn phòng)* | **Có**<br>*(CP1)* | Dán URL chứa IP tĩnh thô `http://45.112.33.199/login` yêu cầu cập nhật IT. | Dán link -> Trả về `DANGER` (Risk Score 95) ngay lập tức (0ms token cost) qua Tầng 1 Rule Engine. Phong gật đầu hài lòng khi thấy badge Rule Hit. | *"Bình thường công ty hay gửi mail cập nhật IT nên mình rất dễ bấm nhầm. Tool chỉ ra rõ dùng IP thô trực tiếp thay vì domain công ty giúp mình tự tin click cancel ngay."* | **Thấp** *(Đúng logic Rule Whitelist/Blacklist)* |
| **3** | **Lê Văn Hoàng**<br>*(Học viên VLearn)* | **Có**<br>*(CP1)* | Dán link rút gọn `bit.ly/3xYpQmZ` nhận được từ tin nhắn làm lại quiz 3 khẩn cấp. | Nhấn quét -> Phản hồi thẻ màu VÀNG `WARNING` (Risk Score 75/100). Hoàng khựng lại phân vân nhìn chỉ số Risk Score 75. | *"Giao diện Warning màu vàng cảnh báo thận trọng khá hay, nhưng lúc đầu em nhìn điểm 75/100 tưởng là 75% an toàn! Nên ghi rõ 'Mức độ rủi ro: 75/100' thay vì chỉ để con số 75 khiến người dùng dễ hiểu nhầm thành Score an toàn."* | **Cao** *(Lỗi hiểu nhầm UX quan trọng về Risk Score)* |
| **4** | **Đỗ Thị Mai**<br>*(Học viên Zone E401)* | **Không** | Dán URL `https://vlearn.vn/lesson-04` chuẩn và link đối tác `partner-company.com/docs`. | URL VLearn trả nhãn XANH `SAFE` tức thì (0ms). Dán link đối tác trả nhãn `WARNING`. Mai muốn lưu lý do nghi vấn để gửi hỗ trợ nhưng không có nút copy. | *"Link chuẩn `vlearn.vn` chạy cực nhanh không tốn giây nào. Còn link đối tác ra màu Vàng thì đúng rồi, nhưng nút copy lý do nghi vấn chưa có, em muốn copy gửi cho TA kiểm tra lại thì phải bôi đen bằng tay."* | **Trung bình** *(Tiện ích giao diện người dùng)* |
| **5** | **Phạm Minh Anh**<br>*(TA / Học viên Zone E403)* | **Không** | Dán URL Open Redirect qua Google: `google.com/url?q=http://malicious-phishing.top`. | Engine v2 bóc tách thành công URL đích `malicious-phishing.top`, gán nhãn `DANGER` (Score 95/100). Minh Anh soi kỹ danh sách `suspicious_elements`. | *"Bắt được cả chiêu Google Open Redirect này là rất xịn! Tuy nhiên phần giải thích lý do (suspicious_elements) nên để dạng bullet points gạch đầu dòng rõ ràng hơn thay vì một đoạn text dài hơi khó đọc lướt."* | **Trung bình** *(Định dạng hiển thị giải thích HAX G11)* |

---

## 📊 3. Tổng Hợp Kết Quả & Quyết Định Hành Động (4 Dòng Tổng Hợp)

1. **Chủ đề lặp nhiều nhất (Most Repeated Issue):**
   - Sự mơ hồ trong cách hiển thị chỉ số rủi ro **Risk Score (75/100)** khiến người dùng bị nhầm lẫn giữa *"75% An toàn"* và *"75% Rủi ro"*, cùng với việc trình bày danh sách lý do nghi vấn (`suspicious_elements`) dạng chuỗi dài gây khó đọc lướt.

2. **Thay đổi thực hiện ngay trước demo (Cập nhật vào Changelog spec §9):**
   - **Cải tiến UI hiển thị Risk Score:** Đổi nhãn hiển thị thành `"Mức độ Rủi ro: 75/100 (WARNING - Thận trọng)"` kèm thanh tiến trình (progress bar) đổi màu linh hoạt theo cấp độ (Xanh cho SAFE, Vàng cho WARNING, Đỏ cho DANGER).
   - **Tối ưu định dạng giải thích:** Chuyển danh sách `suspicious_elements` thành dạng danh sách gạch đầu dòng (bullet points) kèm biểu tượng cảnh báo ⚠️ trực quan (tuân thủ nguyên tắc HAX G11).

3. **Quyết định giữ nguyên có lý do căn cứ:**
   - **Giữ nguyên cơ chế phán quyết 3 lớp (`SAFE` / `WARNING` / `DANGER`):** Không đưa về 2 lớp nhị phân (`Allow` / `Block`) dù một số người dùng ban đầu băn khoăn về nhãn `WARNING`. 
   - *Căn cứ:* Đối với các tên miền rút gọn (`bit.ly`) hoặc tên miền đối tác chưa xác minh, gán nhãn `WARNING` là áp dụng đúng nguyên tắc **HAX G10 (Thu hẹp phạm vi khi nghi ngờ)**, vừa cảnh báo nhắc nhở người dùng nâng cao cảnh giác vừa không chặn nhầm truy cập hợp lệ (giữ chỉ số False Positive Rate FPR = 0.0%).

4. **Đưa vào Backlog cho phát triển tương lai (Phục vụ Slide 6):**
   - Bổ sung nút **"1-Click Copy Báo Cáo"** cho phép người dùng sao chép nhanh kết quả phân tích kèm lý do kỹ thuật để gửi cho bộ phận IT Security / TA.
   - Tích hợp API tự động giải mã liên kết rút gọn (Unshorten API) để bóc tách URL đích thực sự trước khi đưa qua LLM Reasoning Engine.
