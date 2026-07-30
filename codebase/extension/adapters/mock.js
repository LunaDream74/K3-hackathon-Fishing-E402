/* ============================================================================
   ADAPTER THAM CHIẾU — hộp thư giả lập (host "inbox-mock", contract v1)

   Đây là bản hiện thực mẫu của hợp đồng trong DOM-CONTRACT.md.
   Nhiệm vụ DUY NHẤT của adapter: đọc DOM của trang chủ nhà và trả về một
   object thuần. Adapter KHÔNG chấm điểm, KHÔNG gọi LLM, KHÔNG vẽ giao diện.

   Muốn hỗ trợ Gmail thật: copy file này thành adapters/gmail.js, giữ nguyên
   4 hàm export, chỉ đổi phần selector bên trong. Content script không cần
   biết nó đang chạy trên host nào.
   ============================================================================ */

export const HOST_ID = "inbox-mock";

/** Adapter này có dùng được cho trang đang mở không? */
export function matches() {
  return document.body?.dataset.psHost === HOST_ID;
}

function textOf(root, field) {
  const el = root.querySelector(`[data-ps-field="${field}"]`);
  return el ? el.textContent.trim() : "";
}

/**
 * Đọc thư đang mở.
 * @returns {null | {
 *   threadId: string, subject: string, fromName: string, fromAddress: string,
 *   date: string, rawHeaders: string, bodyText: string,
 *   links: {href: string, text: string, el: HTMLAnchorElement}[],
 *   bodyEl: HTMLElement, slotEl: HTMLElement
 * }}
 */
export function readThread() {
  const root = document.querySelector("[data-ps-thread]");
  if (!root) return null;

  const bodyEl = root.querySelector('[data-ps-field="body"]');
  const links = bodyEl
    ? [...bodyEl.querySelectorAll("a[href]")].map((a) => ({
        href: a.getAttribute("href") || "",
        text: a.textContent.trim(),
        el: a,
      }))
    : [];

  return {
    threadId: root.getAttribute("data-ps-thread-id") || "",
    subject: textOf(root, "subject"),
    fromName: textOf(root, "from-name"),
    fromAddress: textOf(root, "from-address"),
    date: textOf(root, "date"),
    // Có thể là "" — xem DOM-CONTRACT.md §5. Gmail thật KHÔNG cho sẵn phần này.
    rawHeaders: textOf(root, "raw-headers"),
    bodyText: bodyEl ? bodyEl.innerText.trim() : "",
    links,
    bodyEl,
    slotEl: root.querySelector('[data-ps-slot="banner"]'),
  };
}

/**
 * Gọi cb mỗi khi người dùng mở sang thư khác.
 * Mở thư trong hộp thư (và trong Gmail) KHÔNG tải lại trang — nếu chỉ đọc
 * một lần lúc khởi động thì tiện ích sẽ đứng im ở thư đầu tiên.
 * @param {(thread: ReturnType<typeof readThread>) => void} cb
 * @returns {() => void} hàm huỷ theo dõi
 */
export function onThreadChange(cb) {
  let lastId = null;

  const tick = () => {
    const t = readThread();
    const id = t?.threadId ?? null;
    if (id !== lastId) {
      lastId = id;
      if (t) cb(t);
    }
  };

  const mo = new MutationObserver(tick);
  mo.observe(document.body, { childList: true, subtree: true });
  tick(); // thư đang mở sẵn lúc tiện ích khởi động

  return () => mo.disconnect();
}

/**
 * Chèn phần tử banner của tiện ích vào đúng chỗ host đã chừa.
 * Luôn thay thế banner cũ để không nhân bản khi người dùng đổi thư qua lại.
 * @param {HTMLElement} el
 */
export function mountBanner(el) {
  const slot = document.querySelector('[data-ps-slot="banner"]');
  if (!slot) return false;
  slot.replaceChildren(el);
  return true;
}
