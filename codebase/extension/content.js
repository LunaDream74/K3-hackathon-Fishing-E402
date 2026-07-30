/* ============================================================================
   CONTENT SCRIPT — đọc thư qua adapter, hỏi service worker, vẽ banner.

   Không chứa logic phát hiện (chuyện đó là của engine v1 sau bridge) và không
   chứa selector riêng của host nào (chuyện đó là của adapter). Ở đây chỉ có
   giao diện + luồng.
   ============================================================================ */
(async () => {
  "use strict";

  const IS_EXT = typeof chrome !== "undefined" && chrome.runtime?.id;

  /* ---- adapter ---- */
  let A;
  if (IS_EXT) {
    A = await import(chrome.runtime.getURL("adapters/mock.js"));
  } else {
    A = window.__PS_ADAPTER; // đường dùng khi test thủ công trong DevTools
  }
  if (!A || !A.matches()) return;

  /* ---- style, tiêm một lần ---- */
  const CSS = `
  .ps-ban{border-radius:6px;overflow:hidden;margin:16px 0;font-family:"Segoe UI",system-ui,sans-serif;
    border:1px solid var(--ps-line);background:var(--ps-bg)}
  .ps-bad{--ps-c:#bf0f1d;--ps-bg:#fdecec;--ps-line:#f2b7b7}
  .ps-warn{--ps-c:#835500;--ps-bg:#fcf3de;--ps-line:#e8cb8d}
  .ps-good{--ps-c:#0a6a3e;--ps-bg:#e4f5eb;--ps-line:#a6d9bd}
  .ps-unk{--ps-c:#4b5566;--ps-bg:#eef0f4;--ps-line:#cfd6e0}
  .ps-top{display:flex;gap:13px;padding:14px 16px;align-items:flex-start}
  .ps-lamp{width:32px;height:32px;border-radius:7px;background:var(--ps-c);color:#fff;flex:none;
    display:grid;place-items:center;font-size:17px;font-weight:700}
  .ps-word{font-family:ui-monospace,Consolas,monospace;font-size:15px;font-weight:700;
    letter-spacing:.05em;text-transform:uppercase;color:var(--ps-c)}
  .ps-say{margin-top:3px;font-size:15px;color:#11151c}
  .ps-ev{border-top:1px solid var(--ps-line);padding:2px 16px 10px;margin:0;list-style:none}
  .ps-ev li{display:grid;grid-template-columns:19px 1fr;gap:10px;padding:9px 0;font-size:14px;
    color:#11151c;border-bottom:1px solid var(--ps-line)}
  .ps-ev li:last-child{border-bottom:0}
  .ps-k{width:18px;height:18px;border-radius:50%;background:var(--ps-c);color:#fff;font-size:11px;
    font-weight:700;display:grid;place-items:center;font-family:ui-monospace,monospace;margin-top:2px}
  .ps-foot{border-top:1px solid var(--ps-line);padding:8px 16px;display:flex;gap:9px;align-items:center;
    flex-wrap:wrap;font-family:ui-monospace,Consolas,monospace;font-size:12px;color:#4b5566}
  .ps-tier{border:1px solid #dbe1ea;background:#fff;border-radius:3px;padding:3px 8px;font-weight:700}
  .ps-tier.local{color:#0a6a3e;border-color:#a6d9bd}
  .ps-tier.cloud{color:#1f34c4;border-color:#1f34c4}
  .ps-cached{border:1px solid #a6d9bd;background:#e4f5eb;color:#0a6a3e;border-radius:3px;
    padding:3px 8px;font-weight:700}
  .ps-wait{margin-left:10px;font-family:ui-monospace,Consolas,monospace;font-size:11.5px;
    font-weight:600;color:#1f34c4;background:#e7eafb;border-radius:10px;padding:2px 9px;
    text-transform:none;letter-spacing:0;animation:ps-pulse 1.4s ease-in-out infinite}
  @keyframes ps-pulse{0%,100%{opacity:1}50%{opacity:.45}}
  @media (prefers-reduced-motion: reduce){.ps-wait{animation:none}}
  .ps-quiet{display:flex;align-items:center;gap:9px;font-size:13px;color:#4b5566;padding:7px 11px;
    border-left:3px solid #0a6a3e;background:#f4f6f9;border-radius:0 4px 4px 0;margin:14px 0;
    font-family:"Segoe UI",system-ui,sans-serif}
  .ps-danger-link{color:#bf0f1d!important;border-bottom:2px solid #bf0f1d;background:#fdecec;
    padding:2px 5px;border-radius:3px;font-weight:600;text-decoration:none!important}
  .ps-gate{position:fixed;inset:0;z-index:2147483647;background:rgba(10,13,18,.72);
    display:grid;place-items:center;padding:20px;font-family:"Segoe UI",system-ui,sans-serif}
  .ps-card{background:#fff;border-radius:8px;max-width:520px;width:100%;padding:22px;
    border-top:5px solid #bf0f1d;box-shadow:0 24px 60px rgba(0,0,0,.5)}
  .ps-card h2{margin:0 0 8px;font-size:20px;color:#bf0f1d}
  .ps-card p{margin:0 0 12px;font-size:15px;color:#11151c}
  .ps-target{font-family:ui-monospace,Consolas,monospace;font-size:13px;background:#fdecec;color:#bf0f1d;
    border:1px solid #f2b7b7;border-radius:4px;padding:9px 11px;word-break:break-all;margin-bottom:14px}
  .ps-acts{display:flex;gap:9px;flex-wrap:wrap;align-items:center}
  .ps-safe-btn{background:#11151c;color:#fff;border:0;border-radius:5px;padding:11px 17px;
    font-size:14.5px;font-weight:700;cursor:pointer}
  .ps-risky-btn{background:transparent;border:1px solid #dbe1ea;border-radius:5px;padding:11px 15px;
    font-size:13.5px;color:#4b5566;cursor:pointer}
  `;
  if (!document.getElementById("ps-style")) {
    const s = document.createElement("style");
    s.id = "ps-style";
    s.textContent = CSS;
    document.head.appendChild(s);
  }

  /* Đúng ba phán quyết, mỗi phán quyết luôn đi kèm ĐỘ TIN CẬY.
     PhishShield đưa bằng chứng và mức tin cậy — quyết định cuối cùng là của người dùng.
     Không có trạng thái thứ tư: mọi ca không kết luận được đều là NGHI VẤN
     với độ tin cậy THẤP, không bao giờ là AN TOÀN. */
  const LEVEL = { DANGER: "ps-bad", DOUBT: "ps-warn", SAFE: "ps-good" };
  const WORD = { DANGER: "Nguy hiểm", DOUBT: "Nghi vấn", SAFE: "An toàn" };
  const LAMP = { DANGER: "!", DOUBT: "?", SAFE: "✓" };
  const norm = (v) => (v in WORD ? v : "DOUBT");

  const esc = (s) =>
    String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

  function buildBanner(r, pending) {
    const v = norm(r.verdict);
    const conf = esc(r.confidence || "?");
    // Trong lúc chờ AI phải nói rõ đây chưa phải kết luận cuối — im lặng dễ bị
    // hiểu nhầm thành "đã kiểm tra xong và không sao".
    const wait = pending
      ? `<span class="ps-wait">đang hỏi AI…</span>`
      : "";

    // An toàn = không làm gì cả: một dòng mảnh, không phải banner.
    // Vẫn nói độ tin cậy, để người dùng biết nên tin kết luận này đến đâu.
    if (v === "SAFE") {
      const q = document.createElement("div");
      q.className = "ps-quiet";
      q.innerHTML =
        `<span style="color:#0a6a3e;font-weight:700">✓</span>` +
        `<span>PhishShield không thấy dấu hiệu bất thường trong thư này.</span>` +
        `<span style="margin-left:auto;font-family:ui-monospace,monospace;font-size:11.5px;color:#0a6a3e">` +
        `độ tin cậy: ${conf} · ${r.tier === "cloud" ? "đã hỏi AI" : "tại chỗ"}</span>`;
      return q;
    }

    const seen = new Set();
    const items = (r.evidence || [])
      .filter((e) => !seen.has(e.text) && seen.add(e.text))
      .map((e, i) => `<li><span class="ps-k">${i + 1}</span><span>${esc(e.text)}</span></li>`)
      .join("");

    const el = document.createElement("div");
    el.className = `ps-ban ${LEVEL[v]}`;
    el.innerHTML =
      `<div class="ps-top"><span class="ps-lamp">${LAMP[v]}</span>` +
      `<div><div class="ps-word">${WORD[v]} · độ tin cậy ${conf}${wait}</div>` +
      `<div class="ps-say">${esc(r.recommendation || "")}</div></div></div>` +
      (items ? `<ul class="ps-ev">${items}</ul>` : "") +
      `<div class="ps-foot"><span class="ps-tier ${r.tier}">` +
      `${r.tier === "cloud" ? "CÓ GỌI AI" : "TẠI CHỖ"}</span>` +
      (r.cached ? `<span class="ps-cached">đã lưu · không gọi lại API</span>` : "") +
      `<span>${esc(r.analysis_source || "")}</span>` +
      `<span style="margin-left:auto">Bạn là người quyết định cuối cùng.</span></div>`;
    return el;
  }

  function gate(href) {
    const g = document.createElement("div");
    g.className = "ps-gate";
    g.innerHTML =
      `<div class="ps-card" role="dialog" aria-modal="true">` +
      `<h2>Khoan đã — liên kết này bị đánh dấu nguy hiểm</h2>` +
      `<p>PhishShield cho rằng trang đích là trang đăng nhập giả.</p>` +
      `<div class="ps-target">${esc(href)}</div><div class="ps-acts">` +
      `<button class="ps-safe-btn">Quay lại, đừng mở</button>` +
      `<button class="ps-risky-btn">Tôi hiểu rủi ro, vẫn mở</button></div></div>`;
    const close = () => g.remove();
    g.querySelector(".ps-safe-btn").addEventListener("click", close);
    g.querySelector(".ps-risky-btn").addEventListener("click", close);
    g.addEventListener("click", (e) => { if (e.target === g) close(); });
    document.body.appendChild(g);
    g.querySelector(".ps-safe-btn").focus();
  }

  /* Bản sao rút gọn của bộ đệm trong background.js, CHỈ dùng cho đường chạy thử
     (khi content script được nạp tay vào DevTools, không qua tiện ích thật).
     background.js mới là bản chính — sửa hành vi thì sửa ở đó trước. */
  const devCache = new Map();
  const DEV_TTL = 15 * 60 * 1000;

  async function ask(text, path) {
    if (!IS_EXT) {
      if (path === "/analyze") {
        const hit = devCache.get(text);
        if (hit && Date.now() - hit.at < DEV_TTL) {
          return { ok: true, data: { ...hit.data, cached: true } };
        }
      }
      const res = await fetch("http://127.0.0.1:8777" + path, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });
      const data = await res.json();
      if (path === "/analyze" && res.ok) devCache.set(text, { data, at: Date.now() });
      return { ok: res.ok, data: { ...data, cached: false } };
    }
    return chrome.runtime.sendMessage({ type: "PS_ANALYZE", text, path });
  }

  /* Engine nhận MỘT chuỗi text và tự dò link bằng regex, nên không được ném
     nguyên header thô vào: hostname của máy chủ nhận thư (vd "mx.example.com"
     trong Authentication-Results) sẽ bị đếm là một đường link lạ và kéo cả thư
     sạch xuống "nghi vấn". Chỉ gửi đúng phần có ý nghĩa.

     PHẠM VI: KHÔNG đọc SPF / DKIM / DMARC. Gmail không cho lấy chúng từ DOM, và
     nhóm cũng không có email thật để mô phỏng cho trung thực — xem DOM-CONTRACT §5.
     Kết luận dựa trên tên miền người gửi, nội dung và đường link. */
  function composeForEngine(t) {
    const lines = [`Chủ đề: ${t.subject}`, `Người gửi: ${t.fromName} <${t.fromAddress}>`];

    // Reply-To khác người gửi là dấu hiệu đọc được ở mọi hộp thư, không cần
    // tới cơ chế xác thực nào — nên vẫn dùng.
    const replyTo = (t.rawHeaders || "").match(/^Reply-?To:[ \t]*(.+)$/im)?.[1];
    if (replyTo) lines.push(`Reply-To: ${replyTo.trim()}`);

    return lines.join("\n") + "\n\n" + t.bodyText;
  }

  /* Mỗi lần mở thư mới là một "thế hệ". Lời gọi LLM mất vài giây, nên nếu
     người dùng bấm sang thư khác giữa chừng, kết quả của thư CŨ sẽ về sau và
     đắp nhầm lên thư ĐANG mở — cảnh báo của thư này hiện trên thư kia.
     Mọi kết quả trả về đều phải qua cửa này trước khi được vẽ. */
  let generation = 0;

  const OFFLINE = (err) => ({
    verdict: "DOUBT", tier: "local", confidence: "THẤP", evidence: [],
    recommendation: "Không kết nối được engine PhishShield. Chưa kiểm tra được thư này — " +
                    "đừng bấm liên kết cho tới khi kiểm tra lại.",
    analysis_source: "BRIDGE UNAVAILABLE: " + (err || "unknown"),
  });

  function paint(r, t, pending) {
    A.mountBanner(buildBanner(r, pending));
    if (r.verdict !== "DANGER") return;
    for (const l of t.links) {
      if (l.el.dataset.psGated) continue;
      l.el.dataset.psGated = "1";
      l.el.classList.add("ps-danger-link");
      l.el.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        gate(l.href);
      });
    }
  }

  async function onThread(t) {
    const mine = ++generation;
    const threadId = t.threadId;

    // Còn đúng thư đã gửi đi hỏi không? Kiểm tra cả thế hệ lẫn id, vì DOM có
    // thể đã bị thay mới hoàn toàn trong lúc chờ.
    const stillCurrent = () =>
      mine === generation && A.readThread()?.threadId === threadId;

    const text = composeForEngine(t);

    // Tầng 1: tức thì, chạy tại chỗ. Người dùng có câu trả lời ngay thay vì
    // đọc thư trong im lặng suốt mấy giây chờ AI.
    let quick;
    try { quick = await ask(text, "/scan"); } catch (err) { quick = { ok: false, error: String(err) }; }
    if (!stillCurrent()) return;

    const first = quick?.ok ? quick.data : OFFLINE(quick?.error);
    paint(first, t, !!first.pending_llm);

    if (!first.pending_llm) return; // tầng 1 đã kết luận — xong

    /* Chờ một nhịp trước khi gọi AI.

       Người dùng lướt hộp thư sẽ mở qua hàng loạt thư trong vài trăm mili giây.
       Nếu gọi ngay, mỗi cái liếc qua là một lần trả tiền — bộ chặn theo
       "thế hệ" chỉ bỏ KẾT QUẢ về muộn, chứ tiền thì đã tiêu rồi.
       Đợi một nhịp ngắn: chỉ thư nào người dùng thật sự dừng lại mới tốn token. */
    await new Promise((r) => setTimeout(r, 450));
    if (!stillCurrent()) return;

    // Tầng 2: hỏi AI, rồi thay kết quả tạm bằng kết luận thật.
    let full;
    try { full = await ask(text, "/analyze"); } catch (err) { full = { ok: false, error: String(err) }; }
    if (!stillCurrent()) return;

    paint(full?.ok ? full.data : OFFLINE(full?.error), t, false);
  }

  A.onThreadChange(onThread);
})();
