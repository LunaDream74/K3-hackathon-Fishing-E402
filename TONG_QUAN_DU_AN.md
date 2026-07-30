# TỔNG QUAN DỰ ÁN HACKATHON AI: PHISHING EMAIL DETECTION ASSISTANT
> **Sự kiện:** Mini Hackathon AI — Batch 03 (Khoá K4 AI Thực Chiến)  
> **Quy trình:** SPEC → Prototype → Demo  
> **Phân công trọng tâm:** Xây dựng và hoàn thiện **"Bộ não của hệ thống" (AI Engine / Risk Reasoning System)**  

---

## 1. Bối cảnh & Bài toán Thực tế (User Pain Story)

### 📌 Kịch bản thực tế
> *Một nhân viên trong công ty nhận được một email với thông báo khẩn cấp (cập nhật mật khẩu / nâng cấp phần mềm bảo mật) trông rất giống email do phòng IT/Kỹ thuật gửi. Do tin tưởng, nhân viên bấm vào đường link đi kèm. Liên kết này dẫn đến một trang web độc hại và khiến hệ thống/tài khoản bị xâm nhập. Sự việc chỉ được phát hiện khi bộ phận Kỹ thuật phát cảnh báo chung về đợt tấn công email lừa đảo (Phishing Email).*

### 🛑 Phân tích Pain Point & Hậu quả
- **Đối tượng chịu ảnh hưởng (User):** Nhân viên văn phòng, nhân sự không có chuyên môn sâu về An toàn thông tin (Cybersecurity).
- **Hành vi vướng mắc:** Không phân biệt được email giả mạo tinh vi (Spear Phishing / Email Spoofing giả danh IT) và email thông báo thật.
- **Tâm lý dễ bị khai thác:** Sự tin tưởng tuyệt đối vào danh nghĩa phòng Kỹ thuật / IT nội bộ, kèm yếu tố thúc ép thời gian (Urgency).
- **Hậu quả nghiêm trọng:** Lộ thông tin đăng nhập, bị cài mã độc/ransomware, làm dấy lên nguy cơ rò rỉ dữ liệu toàn công ty.

---

## 2. Giải pháp Sản phẩm: AI Phishing Protection Assistant

### 🎯 Lát cắt Sản phẩm (Core Slice)
> **Sản phẩm:** Ứng dụng/Trợ lý AI giúp nhân viên kiểm tra, phân tích và phát hiện tức thì xem một email nhận được có phải là Phishing Email hay không trước khi bấm vào bất kỳ đường link nào.

- **Lát cắt 1 câu:**  
  *Một nhân viên nghi vấn email → Tải lên/Dán nội dung & header email → Bộ não AI phân tích tính hợp lệ, phát hiện kịch bản thao túng và quét rủi ro liên kết → Nhận kết quả cảnh báo mức độ rủi ro (An toàn / Nghi vấn / Độc hại) kèm giải thích chi tiết và hướng dẫn xử lý an toàn trong 5 giây.*

---

## 3. Kiến trúc "Bộ não của Hệ thống" (Core AI Engine Architecture)

Là người chịu trách nhiệm chính về **"Bộ não của hệ thống"**, kiến trúc xử lý của AI Engine sẽ bao gồm 4 thành phần nòng cốt:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Nội dung Email & Headers                        │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                     1. Email Parser & Feature Extractor                │
│  - Phân tích Sender Domain vs Display Name (Spoofing Check)            │
│  - Trích xuất URL / Hyperlink (Homograph, Redirect, IP URLs)          │
│  - Phân tích cấu trúc Header (SPF, DKIM, DMARC status nếu có)           │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                  2. Knowledge Base & Context Retriever (RAG)           │
│  - Whitelist domain chuẩn của công ty (ví dụ: @company.com)            │
│  - Mẫu thông báo chuẩn từ phòng IT & quy trình xác thực nội bộ         │
│  - Database các kịch bản Phishing phổ biến & Blacklist URLs           │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│               3. Reasoning & Scoring Engine (LLM + Guardrails)         │
│  - Phân tích Tâm lý học xã hội (Urgency, Fear, Impersonation)         │
│  - Chấm điểm rủi ro Risk Score (0 - 100) & Phân loại Mức độ            │
│  - Giải thích bằng ngôn ngữ tự nhiên, không thuật ngữ quá phức tạp     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│             4. Response Generator & Actionable Recommendation          │
│  - Cảnh báo trực quan (Xanh: An toàn | Vàng: Cảnh báo | Đỏ: Nguy hiểm)  │
│  - Bằng chứng chỉ rõ (Vì sao email này đáng nghi?)                     │
│  - Khuyến nghị bước tiếp theo (Báo cáo IT, Xác minh qua Slack/Phone)   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Xử lý 4 Lớp Chỗ Khó (Hard Spots Taxonomy) của AI Brain

Để đảm bảo Bộ não AI hoạt động tin cậy và không "bị lừa", hệ thống phải giải quyết 4 lớp rủi ro cốt lõi:

| Lớp rủi ro | Thách thức cụ thể | Giải pháp xử lý của Bộ não AI |
|---|---|---|
| **① Nguồn sự thật (Truth Source)** | AI tự bịa đặt (hallucination) tính an toàn của domain/link khi thiếu dữ liệu kiểm tra. | Chỉ kết luận dựa trên đối chiếu Whitelist/Blacklist thực tế và phân tích trực tiếp trên Header/Link trích xuất được. Không phỏng đoán nếu thiếu căn cứ. |
| **② Mơ hồ / Thiếu thông tin (Ambiguity)** | Email chỉ có 1-2 câu ngắn, không có header hoặc link để soi. | Đánh giá mức độ tin cậy thấp (**Low Confidence**), đưa cảnh báo mức Vàng và hướng dẫn người dùng cung cấp thêm thông tin (Forward full header/mail raw). |
| **③ Ngoài thẩm quyền (Scope)** | Người dùng yêu cầu AI: *"Hãy chặn sender này giúp tôi"* hoặc *"Xóa tài khoản lừa đảo"*. | AI từ chối thực hiện hành động hệ thống, giải thích giới hạn thẩm quyền và cung cấp nút/mẫu báo cáo gửi cho IT Admin. |
| **④ Đặc thù Domain Security (Domain Risk)** | **Cost-of-Error cực cao:** Nếu báo nhầm một Phishing Email là "An toàn" (False Negative), hệ thống công ty sẽ bị hack! | Áp dụng chính sách **Bảo thủ An toàn (Pessimistic Safety Guardrails)**. Thà báo nhầm mức Cảnh báo Vàng còn hơn bỏ sót mối nguy Đỏ. |

---

## 5. Kế hoạch Kiểm thử & Đánh giá Bộ não AI (`eval/`)

Để đạt điểm tối đa trong phần **R4 · Kiểm thử (15 điểm)** của Rubric Hackathon, Bộ não AI sẽ được đánh giá nghiêm ngặt:

### 📊 Xây dựng Golden Set (`eval/golden_set.json`)
Cần chuẩn bị **≥ 20 - 30 case test mẫu**, bao gồm các nhóm:
1. **Spear Phishing giả danh IT nội bộ (Cực kỳ tinh vi):** Đổi tên hiển thị `IT Support <hacker@external-domain.com>`, dùng link fake login office.
2. **Email Phishing hàng loạt phổ biến:** Thông báo trúng thưởng, thông báo tài khoản ngân hàng bị khóa.
3. **Email IT xịn thật của công ty:** Email thông báo bảo trì hệ thống thật từ domain chuẩn.
4. **Email Spam / Marketing thông thường:** Quảng cáo dịch vụ, khóa học (không độc hại nhưng phiền phức).
5. **Email ngắn / Mơ hồ:** Thiếu nội dung để thử nghiệm kịch bản Low-confidence.

### 📐 Thước đo Chất lượng (Quality Metrics & Quality Bar)
- **Target Quality Bar:**  
  - **Phishing Detection Recall:** $\ge 95\%$ (Bắt buộc không được bỏ sót email lừa đảo).
  - **Precision:** $\ge 85\%$ (Giảm thiểu báo động giả gây phiền nhiễu cho nhân viên).
  - **Accuracy tổng thể:** $\ge 90\%$ trên toàn bộ Golden Set.
  - **Latency:** Trả kết quả phân tích trong $\le 5$ giây.

---

## 6. Lộ trình Triển khai theo 6 Mốc Checkpoint Hackathon

| Mốc | Thời gian (Khoá 4) | Nhiệm vụ của Bộ não AI & Team | Deliverables |
|---|---|---|---|
| **CP1** | 15:00 Ngày 1 | Chốt Canvas bài toán & Lát cắt sản phẩm | `spec.md` (§1-§2 Canvas nháp) |
| **CP2** | 17:00 Ngày 1 | Xây dựng Flow UI / Prototype bấm được | `codebase/` (Interface & Mock Engine) |
| **CP3** | 10:30 Ngày 2 | **AI Brain chạy thật lượt 1** & Chạy thử trên Golden Set | `eval/` (Lượt chạy 1 & Bảng metrics) |
| **CP4** | 12:00 Ngày 2 | Nộp bản spec.md chính thức (Hạn cứng 23:59 N1) | `spec.md` hoàn chỉnh |
| **CP5** | 14:00 Ngày 2 | User Testing với ≥3 người thật ngoài nhóm & Optimize AI | `validation/` (Feedback log) |
| **CP6** | 15:00 Ngày 2 | Demo trực tiếp & Trình bày Slide (6 trang) | `demo-slides.pdf` & Live Demo |

---

## 7. Cấu trúc Thư mục Nộp bài Repo nhóm

```text
Batch03-K4-AI-Product-Hackathon/
├── README.md              ← Thông tin nhóm & Phân công nhiệm vụ chi tiết
├── TONG_QUAN_DU_AN.md    ← Document tổng quan hệ thống & bộ não AI (File này)
├── spec.md                ← AI Spec đầy đủ 8 phần theo 03-template-ai-spec.md
├── demo-slides.pdf        ← Slide thuyết trình 6 trang
├── codebase/              ← Mã nguồn bộ não AI (Python/LLM Chain) + Frontend Demo UI
├── eval/                  ← Golden set (eval_phishing_cases.json) + Log kết quả kiểm thử
├── validation/            ← User feedback logs từ vòng trải nghiệm thực tế
└── reflection/            ← Bài thu hoạch cá nhân của từng thành viên
```

---

*Hồ sơ này được tổng hợp làm tài liệu định hướng và bộ khung triển khai cho thành viên phụ trách **Bộ não của Hệ thống (AI Core)** trong cuộc thi Hackathon.*
