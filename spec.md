# AI SPEC — Phân Loại Liên Kết Phishing Tiền Truy Cập (PhishShield AI) · NHÓM PHISHSHIELD · ZONE E402
Hướng: [ ] A — VLearn  [ ] B — Trợ lý Học viên  [x] C — Làn mở
Loại: [x] Tính năng mới  [ ] Tối ưu tính năng có sẵn

## §1. User & Job
- **Job executor + workflow:** Học viên khoá học / Nhân viên văn phòng nhận email hoặc tin nhắn chứa đường liên kết (URL) hàng ngày và phân vân xem có an toàn để nhấp vào hay không.
  - *Workflow hiện tại:* Nhận email/tin nhắn -> Nhìn lướt tiêu đề & liên kết -> Đắn đo/Phân vân -> Hoặc nhấp liều (nguy cơ mất tài khoản) hoặc nhờ bên IT/TA kiểm tra hộ (mất thời gian chờ đợi).
- **Core JTBD:** Xác định mức độ an toàn của đường liên kết (URL) trước khi nhấp vào để tránh bị lừa đảo đánh cắp thông tin tài khoản hoặc nhiễm mã độc.
- **Problem statement:** Người dùng thường bị đánh lừa bởi tên miền giả mạo gần giống tên miền chính thức (Typosquatting/Spoofing) và văn bản thúc ép khẩn cấp, dẫn đến việc nhấp vào link độc hại gây lộ mật khẩu và mất quyền truy cập tài khoản.
- **Evidence (chuẩn A và B — log đầy đủ trong repo):**
  - **Số liệu khảo sát & mining (n = 10):** 
    - 7/10 người dùng (70%) xác nhận từng phân vân hoặc nhấp nhầm vào các đường link lạ có chứa từ khóa thúc ép cập nhật tài khoản.
    - 80% các mẫu email lừa đảo thực tế sử dụng tên miền giả mạo cấu trúc TLD rủi ro cao (`.xyz`, `.top`, `.tk`) hoặc URL rút gọn để che giấu đích đến.
  - **≥5 quote/ví dụ nguyên văn + nguồn:**
    1. *"Em thấy email bảo tài khoản spotify sắp hết hạn phải click đổi pass ngay, đuôi link hơi lạ spotify-support.xyz nhưng sợ bị khóa acc nên em bấm đại."* — Lê Văn Tuệ  (Khảo sát người dùng spotify).
    2. *"Nhận được mail thông báo từ IP 45.112.33.199 bảo xác thực đăng nhập, không biết có phải hệ thống công ty nâng cấp không."* — Nguyễn Văn Phong (Nhân viên Văn phòng, Khảo sát người dùng).
    3. *"Ae vào ngay link elearn-quiz-reset.top làm lại bài quiz 3 không là bị 0 điểm nhé."* — Tin nhắn lừa đảo thực tế nhắm vào học viên (Mail trung tâm).
    4. *"Anh ơi link bit.ly/3xYpQmZ này có an toàn không ạ, mail bảo reset mật khẩu gấp."* — Lê Văn Hoàng (Log chatlog).
    5. *"Sếp gửi mail bảo click link ký điện tử hóa đơn gấp finance-vingroup-approval.work/transfer."* — Log mạo danh doanh nghiệp BEC.

## §2. Impact & quyết định chọn
- **Bảng impact ≥3 ứng viên:**
  | Ứng viên tính năng | Bao nhiêu người | Tần suất | Tốn gì mỗi lần | Khả thi | Chọn? |
  |---|---|---|---|---|---|
  | 1. Kiểm tra An toàn URL Tiền truy cập (PhishShield AI) | ~10 học viên/nhân viên | Hàng ngày (2-3 link/ngày) | Rủi ro lộ mật khẩu, mất tài khoản, gián đoạn công việc | Cao (Build được) | **CHỌN** |
  | 2. Tự động lọc & phân loại email spam quảng cáo | ~10 học viên | Hàng tuần | Mất 1-2 phút đọc lướt email rác | Rất cao | Loại |
  | 3. Tự động mã hóa & phân quyền nội dung email | Khối quản trị | Thỉnh thoảng | Mất 5 phút cấu hình khóa bảo mật | Thấp | Loại |
- **Ứng viên ĐÃ LOẠI + vì sao:** 
  - *Ứng viên 2 (Spam Filter):* Tác hại nhỏ, không ảnh hưởng trực tiếp đến an toàn tài sản/tài khoản người dùng.
  - *Ứng viên 3 (Email Encryption):* Phức tạp kỹ thuật cao, vượt quá phạm vi lát cắt prototype trong 1,5 ngày hackathon.
- **Ứng viên CHỌN + vì sao (bằng số):** Chọn **Ứng viên 1 (PhishShield AI)** vì giải quyết rủi ro lớn nhất (nhiều học viên/nhân viên có rủi ro mất tài khoản khi click nhầm), tần suất cao (2-3 link/ngày) và khả thi build prototype end-to-end trong Hackathon.

## §3. Giải pháp tương tự đã nghiên cứu
- **Google Gmail Safe Browsing:** 
  - *Flow:* Cảnh báo banner đỏ khi mở email chứa URL đen đã có trong database.
  - *Đáng học:* Nhận diện nhanh các domain độc hại trong danh sách đen toàn cầu.
  - *Đáng né:* Không giải thích lý do cụ thể vì sao link bị nghi ngờ; không bắt được các tên miền mới tạo giả mạo nội bộ.
  - *Mình khác gì:* Phân tích ngữ cảnh tên miền nội bộ, bóc tách kỹ thuật (Open Redirect, IP thô, Shortener) và đưa ra lý do giải thích bằng Tiếng Việt rõ ràng cho người dùng.
- **Microsoft Defender for Office 365 (Safe Links):** 
  - *Flow:* Kiểm tra và rewrite URL tại thời điểm người dùng click.
  - *Đáng học:* Cơ chế bảo vệ tiền truy cập (Pre-click rewrite).
  - *Đáng né:* Yêu cầu cấu hình hạ tầng doanh nghiệp phức tạp và đắt đỏ, không phù hợp cho người dùng cá nhân.
  - *Mình khác gì:* Giải pháp AI nhẹ nhàng kết hợp Mô hình Lai (Rule Whitelist + LLM Reasoning) phân loại URL ngay lập tức mà không cần cài đặt hạ tầng phức tạp.

## §4. Thiết kế
- **Lát cắt MỘT CÂU:** PhishShield AI đóng vai trò như một extension đưa ra quyết định với 3 mức (SAFE / DANGER / WARNING) kèm lý do giải thích và khuyến nghị hành động trước khi người dùng nhấp truy cập.
- **Non-goals (≥3 thứ KHÔNG build):**
  1. KHÔNG tự động can thiệp hoặc xóa trực tiếp email trong hòm thư riêng của người dùng.
  2. KHÔNG thay thế hệ thống Firewall hay Antivirus toàn cục của doanh nghiệp.
  3. KHÔNG lưu trữ mật khẩu hoặc thông tin cá nhân nhạy cảm của người dùng.
- **Mức prototype nhắm tới:** [x] Working — Tầng 1 Rule-based Whitelist Engine thật + Tầng 2 OpenAI LLM Agent (`gpt-4o-mini`) thật chạy end-to-end.
- **Automation:** [x] conditional — AI tự động phân loại `SAFE` hoặc `DANGER` lập tức qua Tầng Rule-based với các tên miền Whitelist hoặc IP thô/TLD rủi ro cao (0ms, tiết kiệm token cost); chỉ chuyển sang LLM Reasoning khi gặp các liên kết lạ hoặc có ngữ cảnh mơ hồ.
- **§4b. Nguyên tắc đã áp dụng (≥4 — HAX/PAIR):**
  | Nguyên tắc | Áp cụ thể vào đâu trong prototype |
  |---|---|
  | **G1 — Làm rõ hệ thống làm được gì** | Giao diện hiển thị rõ ràng phạm vi: "Đánh giá độ an toàn của đường liên kết URL trước khi truy cập". |
  | **G2 — Làm rõ nó làm tốt đến đâu** | Trả về chỉ số điểm rủi ro Risk Score (0-100) và mức phân loại nguy cơ SAFE / WARNING / DANGER rõ ràng. |
  | **G10 — Thu hẹp phạm vi khi nghi ngờ** | Khi gặp tên miền lạ chưa kiểm chứng hoặc URL rút gọn `bit.ly`, hệ thống gán mức WARNING (Thận trọng) kèm khuyến nghị kiểm tra thêm thay vì phán đoán liều. |
  | **G11 — Giải thích vì sao** | Liệt kê các chi tiết đáng ngờ cụ thể (giả mạo tên miền VLearn, IP thô, TLD rủi ro cao, Open Redirect) trong trường `suspicious_elements`. |

## §5. Kiểu lỗi — 4 lớp chỗ khó + kịch bản (≥8)
| Tình huống cụ thể | Lớp chỗ khó | Hành vi mong muốn (Hệ thống xử lý) | Nguyên tắc áp dụng |
|---|---|---|---|
| 1. URL `vlearn-secure.xyz` giả mạo domain chính thức `vlearn.vn` | ① Nguồn sự thật | Trả về DANGER (Score 95): Cảnh báo tên miền giả mạo VLearn dùng TLD rủi ro cao `.xyz` -> Chặn tiền truy cập. | G11 (Giải thích) |
| 2. URL chứa địa chỉ IP tĩnh thô `http://45.112.33.199/login` | ① Nguồn sự thật | Trả về DANGER (Score 95): Cảnh báo sử dụng IP trực tiếp thay cho tên miền chính thức -> Chặn tiền truy cập. | G2 (Phân loại rõ) |
| 3. URL rút gọn `bit.ly/3xYpQmZ` ẩn giấu điểm đến thực sự | ② Mơ hồ | Trả về DANGER/WARNING (Score 75): Cảnh báo URL rút gọn che giấu điểm đến kèm lời thúc ép khẩn cấp. | G10 (Thu hẹp phạm vi) |
| 4. URL đối tác bên ngoài `partner-company.com/project-docs` | ② Mơ hồ | Trả về WARNING (Score 50): Cảnh báo tên miền đối tác chưa có trong Whitelist, nhắc nhở kiểm tra trước khi bấm. | G10 (Thu hẹp phạm vi) |
| 5. Email/Văn bản thuần chữ không chứa bất kỳ URL nào | ③ Ngoài phạm vi | Trả về SAFE (Score 0): Xác nhận nội dung không chứa liên kết URL nào cần kiểm duyệt. | G1 (Rõ phạm vi) |
| 6. Email chứa cả link chuẩn `vlearn.vn` và link độc hại IP | ③ Ngoài phạm vi | Trả về DANGER (Score 95): Phát hiện ít nhất 1 URL độc hại trong nội dung -> Khuyến nghị không bấm vào link IP. | G2 (Quyết định an toàn) |
| 7. Phishing mạo danh VLearn làm lại bài Quiz `vlearn-quiz-reset.top` | ④ Đặc thù domain | Trả về DANGER (Score 95): Phát hiện tên miền lừa đảo học viên VLearn -> Chặn tránh học viên bị lộ mật khẩu. | G11 (Giải thích) |
| 8. URL portal chính thức `vlearn.vn` hoặc `vinai.io` | ④ Đặc thù domain | Trả về SAFE (Score 0) ngay lập tức qua Tầng Rule-based (0ms token cost) -> Cho qua (Allow). | G2 (Chính xác) |

## §6. Bốn đường đi của trải nghiệm
- **Happy path:** AI phân tích URL `https://vlearn.vn/lesson-04` -> Rule Engine nhận diện Whitelist -> Trả về kết quả `SAFE` (Allow) lập tức (0ms, 0 token cost).
- **Low-confidence (② Mơ hồ):** URL đối tác bên ngoài chưa có trong Whitelist -> Chuyển sang Tầng LLM Reasoning đánh giá -> Trả về kết quả `WARNING` kèm khuyến nghị xác minh trước khi mở.
- **Failure / Không căn cứ (① Giả mạo):** URL giả danh VLearn/VinAI (`vlearn-secure.xyz` hoặc IP `45.112.33.199`) -> Hệ thống phát hiện Typosquatting/IP thô -> Trả về `DANGER` (Block) kèm lý do giải thích chi tiết.
- **Correction (User sửa/Phản hồi):** Người dùng đọc danh sách `suspicious_elements` và khuyến nghị an toàn để tự đưa ra quyết định.

## §7. Kiểm thử
- **Chiều chất lượng + định nghĩa kiểm chứng được:**
  1. *Recall (Độ bao phủ Phishing):* Định nghĩa = TP / (TP + FN). Đo lường tỷ lệ phát hiện đúng các URL lừa đảo độc hại (Mục tiêu ≥ 90.0%).
  2. *False Positive Rate (Tỷ lệ báo nhầm):* Định nghĩa = FP / (FP + TN). Tỷ lệ gán nhầm URL an toàn thành độc hại (Mục tiêu < 5.0%).
  3. *Accuracy (Độ chính xác chung):* Định nghĩa = (TP + TN) / Tổng số cases (Mục tiêu ≥ 90.0%).
  4. *Rule Hit Rate (Tối ưu chi phí):* Tỷ lệ các URL an toàn/độc hại rõ ràng được Tầng 1 Rule Engine xử lý trực tiếp (Mục tiêu ≥ 50.0%).
- **Golden set (≥20 case theo cơ cấu trong guide §2.6, file trong eval/):**
  - Lưu tại [eval/golden_set.json](file:///d:/AI_Vin/LAB/K3-hackathon-Fishing-E402/eval/golden_set.json) gồm **25 mẫu kiểm thử thực tế**.
  - Phủ đủ 4 Lớp Chỗ Khó (4 cases/lớp) & **17/25 cases (68.0%)** bắt nguồn từ quan sát thực tế (Discord khoá học, Chatlog VLearn, Khảo sát người dùng, Email rác thô).
- **Quality bar (chốt từ 23:59, giữ nguyên sau đó):** "Đạt khi ≥ 90.0% qua bộ, Recall ≥ 90.0% và False Positive Rate < 5.0%."
- **Kết quả các lượt chạy (bảng % — cập nhật đến trước CP6):**
  | Lượt chạy | Chế độ | Accuracy | Precision | Recall | False Positive Rate | Rule Hit Rate | File kết quả |
  |---|---|:---:|:---:|:---:|:---:|:---:|---|
  | **Lượt 1 (Rule-only)** | Offline Rule | 80.0% | 100.0% | 61.5% | 0.0% | 100.0% | `eval/runs/run_rule_l1.json` |
  | **Lượt 2 (Live LLM)** | Live `gpt-4o-mini` | **88.0%** | **100.0%** | **76.9%** | **0.0%** | **72.0%** | [eval/runs/latest_run.json](file:///d:/AI_Vin/LAB/K3-hackathon-Fishing-E402/eval/runs/latest_run.json) |

## §8. Phân công & kế hoạch
- **Phân công có tên:**
  - **Nguyễn Hữu Hiếu (MSSV: 2A202601429):** *Xây dựng workflow bài toán, thiết kế agent* — Phân tích luồng nghiệp vụ bài toán lừa đảo tiền truy cập, thiết kế bộ não PhishingAgent theo kiến trúc lai (Hybrid Architecture: Tầng 1 Rule Whitelist Engine + Tầng 2 OpenAI LLM Reasoning Engine) và tinh chỉnh System Prompt.
  - **Nguyễn Hữu Thắng (MSSV: 2A202601435):** *Xây dựng workflow bài toán, eval & spec* — Viết tài liệu AI Spec (`spec.md`), thiết kế bộ dữ liệu Golden Set 25 cases phủ 4 Lớp Chỗ Khó và dữ liệu thực tế, xây dựng script kiểm thử (`run_eval.py`) và lập báo cáo đánh giá hệ thống.
  - **Trần Nguyễn Anh Minh (MSSV: 2A202601475):** *Xây dựng workflow bài toán, UI* — Đóng góp luồng bài toán, thiết kế giao diện tương tác người dùng (UI), trực quan hóa kết quả phân tích mức độ an toàn (SAFE / WARNING / DANGER), hiển thị điểm rủi ro Risk Score và lý do nghi vấn.
- **Willing users (≥3 tên) + kế hoạch vòng validation CP5:**
  - *3 Willing users:* Lê Văn Tuệ (Khảo sát Spotify), Nguyễn Văn Phong (Nhân viên Văn phòng), Lê Văn Hoàng (Học viên).
  - *Kế hoạch CP5:* Giao task dán 10 link nghi vấn ngẫu nhiên vào prototype -> Im lặng quan sát -> Hỏi 3 câu: ① "Điều gì khó chịu/khó hiểu nhất?", ② "Có tin kết quả cảnh báo không — vì sao?", ③ "Có sẵn sàng dùng thật hàng ngày không — vì sao?" -> Nguyễn Hữu Thắng ghi log nguyên văn phản hồi vào `validation/`.
- **Multi-prototype:** So sánh 2 phương án hiển thị:
  - *Phương án A:* Chỉ hiển thị nhãn chung chung `SAFE` / `DANGER`.
  - *Phương án B (Được chọn):* Hiển thị nhãn phân loại + Điểm rủi ro Risk Score (0-100) + Liệt kê lý do nghi vấn cụ thể (`suspicious_elements`).
  - *Lý do chọn:* Phương án B minh bạch và giải thích rõ nguyên nhân (HAX G11), giúp người dùng an tâm trước khi quyết định click.

## §9. Changelog
| Thời điểm | Đổi gì | Vì sao (trỏ về feedback/case nào) |
|---|---|---|
| 2026-07-30 | Nâng cấp Golden Set lên 25 cases (68% real-world data) | Phủ đủ 4 Lớp Chỗ Khó và dữ liệu thực tế theo Rubric R4 |
| 2026-07-30 | Tích hợp PhishingAgent vào `run_eval.py` | Đo lường thực tế hiệu năng Mô hình Lai (Rule + LLM) |
| 2026-07-30 | Bổ sung cơ chế quét Open Redirect & Shorteners | Vá lỗ hổng ca `rare_phish_03` (`google.com/url?q=...`) và `bit.ly` |
| 2026-07-30 | Cập nhật chính sách Pre-click URL Security | Gán `predicted: block` cho các URL nghi vấn `risk_score >= 50` |

