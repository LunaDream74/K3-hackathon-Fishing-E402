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

  const LEVEL = { DANGER: "ps-bad", DOUBT: "ps-warn", SAFE: "ps-good", UNKNOWN: "ps-unk" };
  const WORD = { DANGER: "Nguy hiểm", DOUBT: "Nghi vấn", SAFE: "An toàn", UNKNOWN: "Chưa kết luận" };
  const LAMP = { DANGER: "!", DOUBT: "?", SAFE: "✓", UNKNOWN: "–" };

  const esc = (s) =>
    String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

  function buildBanner(r) {
    // Im lặng khi an toàn: một dòng mảnh, không phải banner.
    if (r.verdict === "SAFE") {
      const q = document.createElement("div");
      q.className = "ps-quiet";
      q.innerHTML =
        `<span style="color:#0a6a3e;font-weight:700">✓</span>` +
        `<span>PhishShield không thấy dấu hiệu bất thường trong thư này.</span>` +
        `<span style="margin-left:auto;font-family:ui-monospace,monospace;font-size:11.5px;color:#0a6a3e">` +
        `${r.tier === "cloud" ? "Đã hỏi AI" : "Kiểm tra tại chỗ"}</span>`;
      return q;
    }

    const seen = new Set();
    const items = (r.evidence || [])
      .filter((e) => !seen.has(e.text) && seen.add(e.text))
      .map((e, i) => `<li><span class="ps-k">${i + 1}</span><span>${esc(e.text)}</span></li>`)
      .join("");

    const el = document.createElement("div");
    el.className = `ps-ban ${LEVEL[r.verdict] || "ps-unk"}`;
    el.innerHTML =
      `<div class="ps-top"><span class="ps-lamp">${LAMP[r.verdict] || "–"}</span>` +
      `<div><div class="ps-word">${WORD[r.verdict] || "—"}</div>` +
      `<div class="ps-say">${esc(r.recommendation || "")}</div></div></div>` +
      (items ? `<ul class="ps-ev">${items}</ul>` : "") +
      `<div class="ps-foot"><span class="ps-tier ${r.tier}">` +
      `${r.tier === "cloud" ? "CÓ GỌI AI" : "TẠI CHỖ"}</span>` +
      `<span>${esc(r.analysis_source || "")}</span>` +
      `<span style="margin-left:auto">độ tin cậy: ${esc(r.confidence || "?")}</span></div>`;
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

  async function ask(text) {
    if (!IS_EXT) {
      const res = await fetch("http://127.0.0.1:8777/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });
      return { ok: res.ok, data: await res.json() };
    }
    return chrome.runtime.sendMessage({ type: "PS_ANALYZE", text });
  }

  /* Engine v1 nhận MỘT chuỗi text và tự dò link bằng regex. Nếu ném nguyên
     header thô vào, nó sẽ coi cả hostname của máy chủ nhận thư
     (vd "mx.example.com" trong Authentication-Results) là một đường link lạ,
     rồi hạ mọi thư — kể cả thư sạch — xuống "chưa kết luận".
     Vì vậy chỉ chuyển những phần thật sự có ý nghĩa, và rút kết quả xác thực
     ra dạng chữ thay vì để nguyên dòng có hostname. */
  function composeForEngine(t) {
    const lines = [`Chủ đề: ${t.subject}`, `Người gửi: ${t.fromName} <${t.fromAddress}>`];

    const raw = t.rawHeaders || "";
    const replyTo = (raw.match(/^Reply-?To:[ \t]*(.+)$/im) || [])[1];
    if (replyTo) lines.push(`Reply-To: ${replyTo.trim()}`);

    const auth = ["spf", "dkim", "dmarc"]
      .map((k) => {
        const m = raw.match(new RegExp(k + "=(\\w+)", "i"));
        return m ? `${k}=${m[1]}` : null;
      })
      .filter(Boolean);
    if (auth.length) lines.push(`Kết quả xác thực: ${auth.join(" ")}`);

    return lines.join("\n") + "\n\n" + t.bodyText;
  }

  async function onThread(t) {
    const text = composeForEngine(t);

    let reply;
    try {
      reply = await ask(text);
    } catch (err) {
      reply = { ok: false, error: String(err) };
    }

    // Bridge hỏng thì nói thẳng, không được im lặng thành "an toàn".
    const r = reply?.ok
      ? reply.data
      : {
          verdict: "UNKNOWN", tier: "local", confidence: "THẤP", evidence: [],
          recommendation: "Không kết nối được engine PhishShield. Chưa kiểm tra được thư này — " +
                          "đừng bấm liên kết cho tới khi kiểm tra lại.",
          analysis_source: "BRIDGE UNAVAILABLE: " + (reply?.error || "unknown"),
        };

    A.mountBanner(buildBanner(r));

    // Đánh dấu liên kết nguy hiểm ngay trong thân thư + chặn tại cú bấm.
    if (r.verdict === "DANGER") {
      for (const l of t.links) {
        l.el.classList.add("ps-danger-link");
        l.el.addEventListener("click", (e) => {
          e.preventDefault();
          e.stopPropagation();
          gate(l.href);
        });
      }
    }
  }

  A.onThreadChange(onThread);
})();
