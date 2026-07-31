/* ============================================================================
   SERVICE WORKER — bên duy nhất được phép nói chuyện ra ngoài.

   Content script chạy chung "thế giới" với trang hộp thư, nên mọi thứ nhạy cảm
   (API key, endpoint) phải nằm ở đây. Content script chỉ gửi text sang và nhận
   kết quả về.

   Hiện tại service worker gọi bridge chạy tại localhost (codebase/bridge.py),
   nơi engine thật sự chạy. Khi nào chuyển sang gọi thẳng OpenAI thì đổi
   BRIDGE_URL thành endpoint thật và đặt key ở đây — KHÔNG bao giờ ở content.js.
   ============================================================================ */

const BRIDGE_URL = "http://127.0.0.1:8777";

/* ---------------------------------------------------------------------------
   BỘ NHỚ ĐỆM — chỉ cho /analyze (đường TỐN TIỀN).

   /scan chạy tại chỗ, ~150ms, không tốn gì → không cần đệm.
   /analyze mới là đường gọi gpt-4o-mini. Mở lại đúng một email đã soi rồi thì
   không có lý do gì phải trả tiền lần nữa.

   Khoá là NGUYÊN VĂN đoạn text gửi đi, không phải threadId và cũng không phải
   hash. Lý do:
     - threadId sai: cùng một thread nhưng nội dung đổi (có thư mới) thì verdict
       phải đổi theo.
     - hash sai ở chỗ khác: đây là bộ đệm cho một quyết định BẢO MẬT. Một lần
       đụng hash hiếm hoi cũng đủ trả nhầm "an toàn" cho một email lừa đảo.
       Text nguyên văn thì không bao giờ đụng nhau.

   Chặn cũ đi bằng hai lớp: giới hạn số mục và hạn dùng. Verdict cũ nguy hiểm
   hơn là không có verdict — thà gọi lại còn hơn tin vào kết luận đã hết hạn.
   Đổi engine thì TĂNG CACHE_EPOCH để bỏ sạch đệm cũ.
   --------------------------------------------------------------------------- */
const CACHE_EPOCH = 1;      // tăng số này mỗi khi engine đổi hành vi
const CACHE_MAX = 50;       // đủ cho một phiên đọc thư, không phình bộ nhớ
const CACHE_TTL_MS = 15 * 60 * 1000;

const cache = new Map();    // text -> { data, at }

function cacheGet(text) {
  const hit = cache.get(text);
  if (!hit) return null;
  if (Date.now() - hit.at > CACHE_TTL_MS) {
    cache.delete(text);
    return null;
  }
  // Đọc lại thì đẩy lên cuối — Map giữ thứ tự chèn, nên mục cũ nhất bị loại trước.
  cache.delete(text);
  cache.set(text, hit);
  return hit.data;
}

function cacheSet(text, data) {
  cache.delete(text);
  cache.set(text, { data, at: Date.now() });
  while (cache.size > CACHE_MAX) cache.delete(cache.keys().next().value);
}

async function callBridge(text, route) {
  const res = await fetch(`${BRIDGE_URL}${route}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  if (!res.ok) throw new Error(`bridge ${res.status}`);
  return res.json();
}

/* Các yêu cầu ĐANG BAY, gộp theo cùng một khoá.

   Bộ đệm chỉ có dữ liệu SAU KHI một lượt gọi xong. Nếu người dùng mở một thư,
   rời đi, rồi quay lại ngay trong lúc lượt gọi đầu chưa về, cả hai lượt đều
   trượt đệm và ta trả tiền hai lần cho đúng một email.

   Đo thực tế cho thấy có lúc không bị, nhưng chỉ vì lượt đầu tình cờ về kịp —
   tức là phụ thuộc vào độ trễ mạng, không phải vào thiết kế. Gộp lại thì
   lượt thứ hai chờ chính lời hứa của lượt đầu, và chỉ có duy nhất một lời gọi. */
const inflight = new Map();   // key -> Promise

async function analyze(text, path = "/analyze") {
  // Chỉ cho phép đúng hai đường, không nhận path tuỳ ý từ content script.
  const route = path === "/scan" ? "/scan" : "/analyze";

  if (route === "/scan") return callBridge(text, route);

  const key = `${CACHE_EPOCH}|${text}`;
  const hit = cacheGet(key);
  if (hit) return { ...hit, cached: true };   // không tốn một token nào

  const pending = inflight.get(key);
  if (pending) return { ...(await pending), cached: true };

  const p = callBridge(text, route).finally(function () { inflight.delete(key); });
  inflight.set(key, p);

  const data = await p;        // lỗi thì ném ra cho cả bên gọi lẫn bên đang chờ
  cacheSet(key, data);
  return { ...data, cached: false };
}

async function callBridgeChat(text, question) {
  const res = await fetch(`${BRIDGE_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, question }),
  });
  if (!res.ok) throw new Error(`bridge chat ${res.status}`);
  return res.json();
}

async function callBridgeOverride(url, verdict, note) {
  const res = await fetch(`${BRIDGE_URL}/override`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url, verdict, note }),
  });
  if (!res.ok) throw new Error(`bridge override ${res.status}`);
  return res.json();
}

chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  if (msg?.type === "PS_CACHE_STATS") {
    sendResponse({ ok: true, data: { size: cache.size, max: CACHE_MAX } });
    return false;
  }
  if (msg?.type === "PS_OVERRIDE") {
    callBridgeOverride(msg.url, msg.verdict, msg.note)
      .then((data) => sendResponse(data))
      .catch((err) => sendResponse({ ok: false, error: String(err.message || err) }));
    return true;
  }
  if (msg?.type === "PS_CHAT") {
    callBridgeChat(msg.text, msg.question)
      .then((data) => sendResponse(data))
      .catch((err) => sendResponse({ ok: false, error: String(err.message || err) }));
    return true;
  }
  if (msg?.type !== "PS_ANALYZE") return false;

  analyze(msg.text, msg.path)
    .then((data) => sendResponse({ ok: true, data }))
    .catch((err) =>
      // Hỏng bridge KHÔNG được im lặng thành "an toàn" — trả lỗi để UI nói thật.
      sendResponse({ ok: false, error: String(err.message || err) })
    );

  return true; // giữ kênh mở cho sendResponse bất đồng bộ
});
