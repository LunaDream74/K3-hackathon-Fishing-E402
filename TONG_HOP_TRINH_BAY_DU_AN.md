# 🛡️ PHISHSHIELD AI: THÀNH LŨY AN NINH MẠNG ĐỒNG CẢM & TRÍ NHỚ ĐỘNG TỰ DIỄN HÓA
**Tài liệu Tổng hợp Hướng dẫn Báo cáo & Trình bày Hội đồng Đánh Giá (Master Pitching & Presentation Guide)**

---

## 🌟 1. TUYÊN THỆ ĐỊNH VỊ & SỨ MỆNH DỰ ÁN (PROJECT IDENTITY & VALUE PROPOSITION)
- **Tên thương hiệu:** **PhishShield AI Agent (v0.8.0)**
- **Slogan:** *"An ninh kiên cố, Giao tiếp đồng cảm, Quyền riêng tư tối thượng, Trí nhớ tự diễn hóa."*
- **Sức mệnh:** Biến Trí tuệ Nhân tạo thành **Cố Vấn An Ninh Mạng cá nhân hóa** ngay trong hộp thư của từng công dân số và doanh nghiệp. PhishShield AI không làm việc dựa trên sự sợ hãi hay báo động ầm ĩ; sản phẩm hoạt động như một chiến tranh bọc thép thầm lặng, sẵn sàng thấu thị mọi kiếp nạn lừa đảo số mạo danh và cung cấp giải pháp hành động tức thời cho người dùng.

---

## 🎯 2. NỖI ĐAU HIỆN TỰ TRÊN VANG TRƯỜNG & LỜI GIẢI ĐỘT PHÁ CỦA PHISHSHIELD AI
| Phương pháp truyền thống & Giải pháp đối thủ | 🛡️ Sự Khác Biệt Đột Phá Của PhishShield AI |
| :--- | :--- |
| **Báo động ầm ĩ, gây hoang mang cho người dùng (Alert Fatigue):** Các bộ lọc hiện tại nháy đỏ liên tục ngay cả với thư thông thường khiến nhân viên ngán ngẩm tắt luôn tiện ích. | **Giao tiếp Cố Vấn Đồng Cảm & "Quiet by Default":** Im lặng tuyệt đối với thư an toàn (chỉ hiện 1 dòng mảnh tinh tế). Khi gặp thư nguy hiểm, giọng văn nhã nhặn thấu đáo thay vì đe dọa. |
| **Đầu tay bất lực trước lừa đảo mới (Zero-Day / Spear Phishing):** Các cổng kiểm soát bằng danh sách tĩnh bị qua mặt hoàn toàn khi kẻ gian thay đổi tên miền nhái bén (Typosquatting) hoặc lồng link rút gọn. | **Phân tích Đồng Quy (Probabilistic Fusion) & Levenshtein:** Kết hợp nhận diện ngữ cảnh thao túng tâm lý (giục giã, dọa khóa tài khoản) cùng thuật toán thấu thị chính tả tên miền rủi ro. |
| **Gọi LLM đám mây bừa bãi (Chậm, Đắt, Rác Quyền Riêng Tư):** Một số giải pháp mới ném toàn bộ email lên ChatGPT/LLM khiến giá Token cao và rò rỉ dữ liệu mật công ty. | **Kiến Trúc Tường Lửa Kép 2 Tầng (Hybrid Two-Tier Architecture):** 100% email được thẩm định sơ bộ tại chỗ (<1ms, 0 Token), chỉ gửi metadata đường link (không gửi toàn bộ nội dung nhạy cảm) khi thật sự cần tư vấn AI. |
| **Cảnh báo xong... bỏ mặc người dùng:** Hầu hết công cụ chỉ hô "Nguy hiểm!" nhưng không dạy người dùng bước tiếp theo phải làm gì, ai bảo trợ, liên hệ ai. | **Universal Actionable Copilot Drafts:** 100% tình huống (An toàn, Nghi vấn, Độc hại) đều được tự động soạn bản nháp tin nhắn xử lý lý tưởng (gửi IT Helpdesk, xác minh đồng nghiệp...). |
| **Mô hình AI "Hóa thạch", không học theo trải nghiệm (Static Knowledge):** Người dùng có bấm "Báo cáo" trăm lần thì hệ thống vẫn mù quáng ở lượt mở thư tiếp theo. | **Self-Evolving Active Memory (Trí Nhớ Động RLHF):** Khi người dùng ghi nhận phán xét (Mark Safe/Phishing), AI nạp ngay vào trí nhớ thực chiến để phân định lập khắc (<1ms, 0 Token) cho toàn tổ chức ở những lượt sau. |

---

## 💎 3. CHẢY XƯƠNG CỘT CÔNG NGHỆ: 7 ĐIỂM NHẤN CHINH PHỤC BAN GIÁM KHẢO

### ①. Kiến Trúc 2 Tầng Kép Kiên Cố (Hybrid Two-Tier Engine - `url_scanner.py` & `agent.py`)
- **Tầng 1 (Smart Rule Engine 2.0 & Local Guard):** Hoạt động trực tiếp trên máy người dùng. Ứng dụng lý thuyết Zero-Trust, so sánh vân tay Levenshtein chống Typosquatting (phát hiện mượt mà các nhái bén như `vi.n-ai.vn`, `viet-combank.com.vn`), tự động xử lý ngay lập tức mà **không cần kết nối internet, không tiêu tốn một chi phí Token nào!**
- **Tầng 2 (Cloud LLM Reasoning - `gpt-4o-mini`):** Khi và chỉ khi Tầng 1 gặp kịch bản ngụy trang tối tân chưa thể ra phán xét quyết đoán (`needs_llm_call = True`), Trợ lý mới kêu gọi sức mạnh LLM để phân tích hành vi và chủ đích ngầm, thâu tóm chứng cứ sắc lẹm.

### ②. Khiên Bảo Mật Zero-Trust Armor & Sandboxed URL Inspection (`_shared.py` & `url_scanner.py`)
- **Thấu thị Link Rút Gọn (Redirect & Shorteners Unmasking):** Không để các dịch vụ rút gọn (`bit.ly`, `tinyurl`...) che mắt! Hệ thống tích hợp công cụ giải mã chuyển hướng trong hầm cách ly (timeout 3 giây).
- **Tường Lửa Chống Lợi Dụng (Scheme & Anti-SSRF Firewall):** Từ chối lập tức các đường link sai lệch chuẩn như `file:///c:/windows...`, `ftp://` hoặc lừa gạt chèo kéo vào IP hạ tầng mạng nội bộ (SSRF, Localhost, Cloud Metadata).

### ③. Thuật Toán Phán Đoán Đồng Quy (Social Engineering Probabilistic Fusion)
- Trong văn bản lừa đảo hiện đại, kẻ gian cực kỳ hay dùng từ khóa giục giã (*"khẩn", "trong vòng 24h", "khóa tài khoản"*). Bộ máy PhishShield tự động lượng hóa cấp độ đe dọa tâm lý làm **Bộ số nhân rủi ro (Risk Multiplier)** để đánh giá chéo cùng mức độ đáng ngờ của đường link.

### ④. Bản Nháp Hành Động Cho Mọi Tình Huống (Universal Actionable Copilot Toolkit)
- Khắc phục vĩnh viễn hạn chế của các giải pháp khác. Với từng loại kết quả phán xét, hệ thống cung cấp sẵn:
  - **DANGER:** Nhát chém ngắt chuỗi rủi ro + Nháp tin nhắn báo cáo khẩn mang chứng cứ tới phòng IT Security.
  - **DOUBT (Nghi Vấn):** Nháp tin nhắn hỏi xác minh nhã nhặn qua Zalo/kênh giao tiếp chính thức với phòng ban gửi.
  - **SAFE:** Nháp phản hồi xác nhận đã đọc thông báo tới đối tác một cách chuyên nghiệp.

### ⑤. Trợ Lý Hỏi Đáp Thông Minh Trong Email (Interactive Cybersecurity Chatbot)
- Không chỉ dừng lại ở cảnh báo một chiều! Người dùng có thể trò chuyện trực tiếp qua endpoint `/chat` với Trợ lý ngay tại khung hiển thị thư (Collapsible Chat UI).
- Gắn **2 Lớp Khiên An Toàn Vận Hành (Guardrails):**
  1. **Rule-Anchored Truth:** Ngăn Trợ lý bị thao túng lời cắn (Prompt Injection) hay tán thành liên kết bị Tầng 1 từ chối.
  2. **Scope Guardrail & Budget Control:** Tự động né tránh các câu hỏi ngoài phạm vi an ninh mạng, bảo bọc tài nguyên Token tài chính cho công ty.

### ⑥. ĐỔI MỚI ĐỈNH CAO: Trí Nhớ Động Tự Diễn Hóa (Self-Evolving Active Memory via Human RLHF - v0.8.0)
- Thiết lập cơ sở dữ liệu học tập liên tục `codebase/company_policy/active_memory.json`.
- Trao quyền quyết định cho con người (Human-in-the-Loop Override). Khi chuyên viên nghiệp vụ hoặc người dùng can thiệp bấm nút **`[✔️ Mark Safe]`** hoặc **`[🚨 Mark Phishing]`**, Trợ lý ngay lập tức tiếp thu tri thức đó vào danh sách **Active Memory**.
- **Tiêu chuẩn Thực Chiến:** Ở các lần xử lý sau của toàn bộ tập thể nhân viên, hệ thống sẽ chẩn đoán ngay lập tức dựa trên trải nghiệm con người với tốc độ **< 1ms và chi phí 0 Token**, giảm tối đa tỷ lệ báo động giả (False Positives/Negatives)!

### ⑦. Giao Diện Tinh Tế Cực Hạn (Quiet UX & Click Interstitial Gate - `phishshield-extension.html`)
- Thiết kế giao diện như một vị khách hiếu lễ trong hộp thư thầm lặng của người dùng ("Quiet by Default").
- Tích hợp chốt chặn cuối cùng tại đúng khoảnh khắc nguy hiểm: **Cú bấm chuột (Click Gate Interstitial)**. Khi người dùng sơ ý ấn vào link độc hại, màn hình chắn trong suốt toàn dải lập tức bao phủ, phân tích lý do chặn và ranh giới tự do quyết định đầy tính tôn trọng.

---

## 📊 4. BỘ ĐO LƯỜNG SỐ LIỆU & KIỂM CHỨNG KÉP (BENCHMARKS & VALIDATION)

### 📈 4.1. Đánh Giá Khách Quan Trên Bộ Nghiệp Vụ (Automated Vulner-Eval Harness)
- **Cấu trúc bộ thử nghiệm (`eval/`):** Xây dựng bộ thử nghiệm khắc nghiệt 28 kịch bản bao quát: *Typosquatting phức tạp, Obfuscation chèn mồi bẫy tâm lý, Zero-day mạo danh ngân hàng (Vietcombank/VPBank), và Quản trị hệ thống IT.*
- **Kết quả Thực Trạng Lịch Sử (v0.7.0 Live Run):**
  - **Độ chính xác (Accuracy):** **27 / 28 ca (đạt 96.4%)** — Vô cùng tự hào khi vượt xa tiêu chuẩn đề ra ban đầu (Accuracy ≥ 90%, Recall ≥ 95%).
  - **Độ kiểm soát chi phí (Token Optimization):** Tinh giảm trên **75%** lượng Token toàn mạch nhờ pháo đài Tầng 1 và tới **100%** trên các kịch bản có Trí Nhớ Động phong tỏa.
  - *Ghi chú:* 1 ca chưa khớp tuyệt đối 100% do tình trạng trễ nhịp đường kết nối mạng ngoại vi (Timeout nghẽn mạch) ở khâu kiểm thử link rút gọn, và đã được khắc phục hoàn toàn tại v0.8.0 với luật phát hiện Shorteners định danh tại chỗ!

### 🗣️ 4.2. Trích Dẫn Thực Tế Từ Kiểm Tra Người Dùng (External User Validation)
Nhóm đã mời thử nghiệm và phỏng vấn nguyên văn các cá nhân, đáp ứng 100% tiêu chí báo cáo thực chiến của BTC Hackathon:
> **1. Anh Hoàng Nam (Chuyên viên IT Helpdesk):** *"Giao diện cảnh báo hiện ngay trên email rất trực quan và có tính ứng dụng cao cho doanh nghiệp. Khả năng tự động phân tích đường link bất thường kết hợp với soạn thảo văn bản phản hồi nhanh giúp bộ phận kỹ thuật tiết kiệm rất nhiều thời gian hỗ trợ nhân viên."*
> 
> **2. Chị Mai Phương (Trưởng nhóm Marketing):** *"Trước đây nhận email lạ dọa khóa tài khoản là tôi hay bị mất bình tĩnh mà ấn lung tung. Trợ lý AI này giải thích nguy cơ bằng ngôn ngữ dễ hiểu, nhẹ nhàng, đặc biệt là tính năng chặn ngay khi lỡ bấm vào liên kết xấu giúp tôi an tâm tuyệt đối."*

---

## 🎬 5. KỊCH BẢN ĐẠO diễn TRÌNH DIỄN DEMO TRƯỚC GIÁM KHẢO (PITCHING HACK)

> *Thời lượng lý tưởng: 5 Phút (2 Phút Bối cảnh + Kiến trúc | 2.5 Phút Demo Giao Diện & Tính Năng | 0.5 Phút Lộ trình Mở Rộng)*

### 🚀 Bước 1: Khởi Chạy Màn Hình & Trình Bày Giao Diện Mẫu
- **Mở trình duyệt:** Chuyển sang khung mô phỏng trang trọng `phishshield-extension.html` (được xây dựng chuẩn Pixel-perfect với hệ mầu HSL tinh tế và độ tương phản > 7:4:1).
- **Lời dẫn:** *"Kính chào Hội đồng! Dưới đây là diện mạo thực chiến của Trợ lý PhishShield AI khi tích hợp trực tiếp vào hộp thư làm việc của người dùng."*

### 🔥 Bước 2: Trình Diễn "Sự Tinh Tế Của Yên lặng" & Cảnh Báo Đồng Cảm
- **Bấm nút chuyển kịch bản phía trên đê cho khán giả thấy rõ:**
  1. Bấm **`[An toàn — im lặng]`**: Chỉ vào dải nơ nhỏ mảnh xanh mộc mạc phía dưới mục người gửi. *"Thưa Giám khảo, một sản phẩm bảo mật xuất sắc là sản phẩm biết yên lặng! Khi email an toàn, chúng tôi không gây hoang mang hay rắc rối cho mắt nhìn của người dùng."*
  2. Bấm **`[Nghi vấn]`**: Chỉ vào khung màu nhã nhặn. Giải thích về gợi ý nháp tin nhắn để hỏi han đồng nghiệp.
  3. Bấm **`[Nguy hiểm]`**: Đi sâu vào trường hợp email đe dọa chớp nhoáng (khóa trong 30 phút). Chỉ rõ các bằng chứng do công cụ AI bóc trần.

### 🛑 Bước 3: Trình Diễn Khiên Bảo Vệ Cuối Cùng (Click Interstitial Gate)
- **Thao tác:** Bấm thẳng vào đường link nguy hiểm `https://vinai-verify-account.tk/login-secure` trên nội dung email giả định.
- **Hiển thị:** Khung chắn an ninh mờ xám giáp mặt bao phủ (Dialog Gate).
- **Lời dẫn:** *"Mời Giám khảo quan sát khoảnh khắc quyết định nhất! Dù người dùng có bất cẩn bấm nhầm, PhishShield vẫn lập hàng rào ngăn ngặt, giữ cho trang mạo danh không bao giờ được phép khởi chạy, nhưng đồng thời vẫn tôn trọng quyền chủ sở hữu bản thân với nút 'Quay lại' đầy dứt khoát."*

### 🧠 Bước 4: Trình Diễn Tính Năng Mới Nhất: Trí Nhớ Động Tự Diễn Hóa (Human RLHF)
- **Thao tác:** Khách mời/Hội đồng để ý tới dải điều khiển dưới cùng trong bảng cảnh báo có thẻ **`🧠 Active Memory (RLHF)`**.
- Bấm vào nút **`[🚨 Mark Phishing]`** hoặc **`[✔️ Mark Safe]`**.
- Màn hình thông báo hiện chớp: Trợ lý AI lập tức báo thu nhận tín hiệu phản hồi và tiến hành phong tỏa hoặc phê duyệt tên miền vào cơ quan Trí Nhớ Động (`active_memory.json`).
- **Lời dẫn chốt ngã ngũ:** *"Đây là tính năng độc nhất của PhishShield: Sự tiến hóa từ kinh nghiệm người dùng. Khi các chuyên viên IT hoặc Giám đốc xác quyết 1 tên miền, hệ thống Trí Nhớ Động thu nhận tri thức lập tức! Kể từ giây phút sau, bất kỳ nhân sự nào trong công ty mở email tương tự, Tầng 1 sẽ xử lý trong chưa đầy 1 mili-giây, không tốn 1 đồng Token tiền Cloud AI nào cho tổ chức!"*

---

## 🔮 6. LỘ TRÌNH PHÁT TRIỂN & TIỆM CẬN SẢN PHẨM HOÀN HẢO (FUTURE ROADMAP)
- **Pha 1 (Hoàn thành - Hiện nay):** Hệ thống thấu thị kép Trí Nhớ Động RLHF + Bộ công cụ hành động hóa (Universal Drafts) + Trợ lý Hỏi Đáp Trong Thư.
- **Pha 2 (Tương lai gần - Mở rộng quy mô Doanh nghiệp):**
  - **SOAR Security Integration:** Mở cổng Webhooks tự động cảnh báo theo gian gian thực gửi về Trung tâm vận hành An ninh (SOC) hoặc Microsoft Sentinel của doanh nghiệp khi nổ ra làn sóng tấn công đồng loạt (Spear-Phishing Campaign).
  - **Threat Intelligence Pool:** Mạng lưới liên kết dữ liệu Trí Nhớ Động (Active Memory Sync) cho phép nhiều chi nhánh công ty chia sẻ nhãn hiệu bảo bọc theo đường truyền mã hóa đồng thời.
  - **Custom SLM Finetuning:** Sử dụng kho dữ liệu nhãn `active_memory.json` và bộ 28 case thử nghiệm khắc nghiệt để finetune ra một mô hình Ngôn ngữ Nhỏ (Small Language Model - 2B parameters) chạy offline hoàn toàn ngay trong CPU vi mạch máy tính văn phòng của khách hàng!

---

### 📂 THỐNG TÊ ĐỘ GẮN KẾT CÁC TỔ KIỆN TRONG HỆ THỐNG CODEBASE
1. `codebase/agent.py`: Trạng thái Tầng 2 LLM Reasoning + Copilot Chat + Guardrail.
2. `codebase/tools/_shared.py`: Quản lý CSDL White/Blacklist + Bộ xử lý Trí Nhớ Động `load/update_active_memory()`.
3. `codebase/tools/url_scanner.py`: Trái tim Smart Rule Engine 2.0 (Zero-Trust, Levenshtein, Probabilistic Fusion, Active Memory checking).
4. `codebase/bridge.py`: Cầu nối HTTP tốc độ cao kết nối Chrome UI và AI Engine, trang bị endpoint `POST /override` tiếp nhận lệnh RLHF.
5. `phishshield-extension.html`: Kiệt tác Giao diện Trải nghiệm Tối thượng cho phần thử nghiệm lâm sàng và Pitching!
6. `eval/`: Tổ hợp 28 ca rà soát gắt gao chất lượng và báo cáo v0.7.0 Live Run.
7. `my_workspace/`: Trung tâm quản trị tiến trình và nhật ký phát triển kiên trì theo từng milestep của kỹ sư AI.

*Trân trọng cảm ơn Ban Giám Khảo và Khách mời! Chúng tôi sẵn sàng bứt phá và bảo trợ an toàn không gian mạng của bạn! 🛡️🚀*
