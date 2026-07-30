# Hợp đồng DOM — tiện ích PhishShield ↔ trang hộp thư

**Phiên bản: 1** · Host tham chiếu: `inbox.html` (`data-ps-host="inbox-mock"`)

Tài liệu này định nghĩa **ranh giới duy nhất** giữa tiện ích PhishShield và trang
hộp thư mà nó tiêm vào. Giữ đúng ranh giới này thì đổi host (hộp thư giả lập →
Gmail thật) chỉ phải viết lại **một file adapter**, không đụng tới phần còn lại
của tiện ích.

---

## 1. Nguyên tắc

| Bên | Được làm | Không được làm |
|---|---|---|
| **Host** (`inbox.html`) | Hiển thị thư, chừa sẵn chỗ cho banner | Không chứa bất kỳ mã PhishShield nào |
| **Adapter** | Đọc DOM, trả về object thuần | Không chấm điểm, không gọi LLM, không vẽ UI |
| **Content script** | Phân tích, dựng banner, chặn cú bấm | Không tự truy vấn DOM của host |

Nói ngắn: **chỉ adapter biết host trông như thế nào.** Nếu bạn thấy
`document.querySelector` với class của Gmail nằm ngoài `adapters/`, đó là bug.

---

## 2. Thuộc tính host phải cung cấp

Đặt trên `<body>`:

| Thuộc tính | Giá trị | Ý nghĩa |
|---|---|---|
| `data-ps-host` | `"inbox-mock"` | Adapter nào nhận trang này |
| `data-ps-contract` | `"1"` | Phiên bản hợp đồng |

Trong khung đọc thư:

| Selector | Bắt buộc | Nội dung |
|---|---|---|
| `[data-ps-thread]` | ✅ | Bọc toàn bộ thư đang mở |
| `[data-ps-thread-id]` | ✅ | ID thư — **đổi giá trị = đã mở thư khác** |
| `[data-ps-field="subject"]` | ✅ | Tiêu đề |
| `[data-ps-field="from-name"]` | ✅ | Tên hiển thị người gửi |
| `[data-ps-field="from-address"]` | ✅ | Địa chỉ email người gửi |
| `[data-ps-field="date"]` | ➖ | Thời gian |
| `[data-ps-field="body"]` | ✅ | Thân thư; mọi `a[href]` bên trong là liên kết cần soi |
| `[data-ps-field="raw-headers"]` | ➖ | Header gốc — **xem §5** |
| `[data-ps-slot="banner"]` | ✅ | Chỗ trống để tiện ích chèn banner |

---

## 3. Giao diện adapter

Mỗi adapter export đúng 4 thứ. `gmail.js` phải cùng chữ ký với `mock.js`:

```js
export const HOST_ID;                    // string
export function matches(): boolean;      // adapter này dùng được cho trang hiện tại?
export function readThread(): Thread|null;
export function onThreadChange(cb): () => void;   // trả về hàm huỷ theo dõi
export function mountBanner(el): boolean;
```

`Thread` trả về:

```js
{
  threadId, subject, fromName, fromAddress, date,
  rawHeaders,          // "" nếu host không cho — KHÔNG được coi là "đạt"
  bodyText,            // innerText, đã trim
  links: [{ href, text, el }],
  bodyEl, slotEl       // để content script gạch chân / chèn banner
}
```

---

## 4. Mở thư không tải lại trang

Đây là phần **dễ làm sai nhất**, nên host cố tình mô phỏng đúng như Gmail:
bấm sang thư khác **thay DOM tại chỗ**, không có `page load` nào cả.

Hệ quả: đọc DOM một lần lúc khởi động là sai — tiện ích sẽ đứng im ở thư đầu
tiên. Phải theo dõi bằng `MutationObserver`.

⚠️ **So theo PHẦN TỬ, đừng so theo `threadId`.** Đây là lỗi đã thực sự xảy ra:
mở lại đúng thư đang mở thì `threadId` không đổi, nên adapter không báo gì —
trong khi host đã dựng lại toàn bộ khung đọc, tức là chỗ chèn banner mới toanh
và **trống**. Banner biến mất, không ai vẽ lại, người dùng tưởng tiện ích chết.

Phần tử `[data-ps-thread]` bị thay mới mỗi lần khung đọc dựng lại, nên so theo
phần tử bắt được cả hai trường hợp: đổi thư, và mở lại cùng một thư.
`mountBanner()` chỉ thay con bên trong nên không tự kích hoạt lại chính nó.
Xem bản hiện thực trong `codebase/extension/adapters/mock.js`.

Viết adapter cho hộp thư giả lập này mà chạy đúng thì sang Gmail gần như
không phải sửa logic, vì bài toán y hệt.

---

## 5. Phạm vi: KHÔNG kiểm tra SPF / DKIM / DMARC

**Đã chốt (2026-07-30): xác thực header nằm NGOÀI phạm vi.**

PhishShield kết luận dựa trên **tên miền người gửi, nội dung, và đường link**.
Không dùng SPF/DKIM/DMARC.

Vì sao chốt như vậy:

- **Gmail không cho lấy.** `Authentication-Results` không nằm trong DOM — nó ở sau
  *"Hiển thị bản gốc"*, tại một URL khác (`?view=om`). Muốn có thì phải xin thêm
  quyền hoặc đi qua Gmail API + OAuth. Quá nặng so với giá trị mang lại ở phạm vi bài này.
- **Không mô phỏng trung thực được.** Nhóm không có email thật với header xác thực
  thật, nên mọi `spf=fail` trong bộ test đều là do mình tự viết ra. Đo một thứ tự
  mình bịa thì con số không nói lên điều gì.

Không phải "sắp có". Đây là **giới hạn được khai báo**, ghi rõ trong `spec.md`.
Guardrail sẵn có đã xử lý đúng: thiếu dữ liệu thì hạ độ tin cậy, không đoán liều.

> `[data-ps-field="raw-headers"]` vẫn còn trong host giả lập và vẫn là **tuỳ chọn**.
> Adapter cứ đọc nếu có, nhưng **không được coi là điều kiện bắt buộc** — Gmail sẽ
> trả về `""`, và mọi thứ vẫn phải chạy đúng.

Khác biệt còn lại giữa host giả lập và Gmail:

| | Host giả lập | Gmail thật |
|---|---|---|
| Selector | `data-ps-*`, ổn định | class rối, đổi bất thường |
| Thư trong chuỗi | 1 thư / 1 thread | nhiều thư, có thư bị gập |
| Thân thư | HTML thẳng | nằm trong `iframe` ở một số chế độ |
| Header xác thực | có sẵn (tuỳ chọn) | không có — **và không dùng đến** (xem §5) |

---

## 6. Chạy thử

Content script **không chạy trên `file://`** trừ khi bật thủ công
*"Allow access to file URLs"* cho từng tiện ích. Luôn phục vụ qua HTTP:

```bash
cd codebase/extension-host
python -m http.server 8931
# mở http://localhost:8931/inbox.html
```

`manifest.json` khớp cả hai host:

```json
"content_scripts": [{
  "matches": ["http://localhost:8931/*", "https://mail.google.com/*"],
  "js": ["content.js"]
}]
```

Kiểm tra hợp đồng mà chưa cần tiện ích: mở DevTools Console trên `inbox.html`,
dán `verify-contract.js`. Nó in ra đúng những gì adapter đọc được.

---

## 7. Bảo mật — không thương lượng

- **API key nằm ở `background.js` (service worker), tuyệt đối không ở content
  script.** Content script chạy chung thế giới với trang; để key ở đó là công
  khai key trên chính trang hộp thư.
- Content script gửi `chrome.runtime.sendMessage` sang service worker; service
  worker mới là bên gọi OpenAI. Làm vậy cũng tránh luôn CORS.
- Tầng luật tĩnh chạy **hoàn toàn tại chỗ**, không phát ra request nào — đó là
  điều kiện để nhãn `TẠI CHỖ` trên banner là thật. Chỉ khi
  `needs_llm_call = true` mới được gửi đi, và chỉ gửi header + đường link,
  không gửi cả thân thư.
