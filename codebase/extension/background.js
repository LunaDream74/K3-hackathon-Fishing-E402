/* ============================================================================
   SERVICE WORKER — bên duy nhất được phép nói chuyện ra ngoài.

   Content script chạy chung "thế giới" với trang hộp thư, nên mọi thứ nhạy cảm
   (API key, endpoint) phải nằm ở đây. Content script chỉ gửi text sang và nhận
   kết quả về.

   Hiện tại service worker gọi bridge chạy tại localhost (codebase/bridge.py),
   nơi engine v1 thật sự chạy. Khi nào chuyển sang gọi thẳng OpenAI thì đổi
   BRIDGE_URL thành endpoint thật và đặt key ở đây — KHÔNG bao giờ ở content.js.
   ============================================================================ */

const BRIDGE_URL = "http://127.0.0.1:8777";

async function analyze(text, path = "/analyze") {
  // Chỉ cho phép đúng hai đường, không nhận path tuỳ ý từ content script.
  const route = path === "/scan" ? "/scan" : "/analyze";
  const res = await fetch(`${BRIDGE_URL}${route}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  if (!res.ok) throw new Error(`bridge ${res.status}`);
  return res.json();
}

chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  if (msg?.type !== "PS_ANALYZE") return false;

  analyze(msg.text, msg.path)
    .then((data) => sendResponse({ ok: true, data }))
    .catch((err) =>
      // Hỏng bridge KHÔNG được im lặng thành "an toàn" — trả lỗi để UI nói thật.
      sendResponse({ ok: false, error: String(err.message || err) })
    );

  return true; // giữ kênh mở cho sendResponse bất đồng bộ
});
