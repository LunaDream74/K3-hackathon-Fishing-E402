/* ============================================================================
   CONTENT SCRIPT — V0.5.0: HUMAN-IN-THE-LOOP VERDICT OVERRIDE & ACTIONABLE UX
   Đọc thư qua adapter, hỏi service worker/bridge, hiển thị bản nháp AI, 
   và cho phép Người Dùng (Chốt Chặn Cuối Cùng) chuyển trạng thái email tháo khóa link!
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
  .ps-say{margin-top:4px;font-size:15px;color:#11151c;line-height:1.45}
  .ps-ev{border-top:1px solid var(--ps-line);padding:2px 16px 10px;margin:0;list-style:none}
  .ps-ev li{display:grid;grid-template-columns:19px 1fr;gap:10px;padding:9px 0;font-size:14px;
    color:#11151c;border-bottom:1px solid var(--ps-line);line-height:1.4}
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
  .ps-quiet{display:flex;flex-direction:column;gap:6px;font-size:13px;color:#4b5566;padding:10px 14px;
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
  .ps-interactive-btn{transition:all .2s ease;cursor:pointer}
  .ps-interactive-btn:hover{opacity:0.92;transform:translateY(-1px);box-shadow:0 2px 5px rgba(0,0,0,.12)}
  `;
  if (!document.getElementById("ps-style")) {
    const s = document.createElement("style");
    s.id = "ps-style";
    s.textContent = CSS;
    document.head.appendChild(s);
  }

  /* ---- CƠ CHẾ QUẢN TRỊ OVERRIDE CỦA NGƯỜI DÙNG (HUMAN-IN-THE-LOOP MEMORY) ---- */
  const OVERRIDE_KEY = "ps_human_verdict_overrides";
  function getOverrides() {
    try { return JSON.parse(localStorage.getItem(OVERRIDE_KEY) || "{}"); } catch (e) { return {}; }
  }
  function setOverride(threadId, verdict) {
    const o = getOverrides();
    if (verdict === null || verdict === undefined) delete o[threadId];
    else o[threadId] = verdict;
    try { localStorage.setItem(OVERRIDE_KEY, JSON.stringify(o)); } catch (e) {}
  }

  const LEVEL = { DANGER: "ps-bad", DOUBT: "ps-warn", SAFE: "ps-good" };
  const WORD = { DANGER: "Nguy hiểm", DOUBT: "Nghi vấn", SAFE: "An toàn" };
  const LAMP = { DANGER: "!", DOUBT: "?", SAFE: "✓" };
  const norm = (v) => (v in WORD ? v : "DOUBT");

  const esc = (s) =>
    String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

  function buildBanner(r, pending, t) {
    const ov = t ? getOverrides()[t.threadId] : null;

    // TRƯỜNG HỢP 1: NGƯỜI DÙNG ĐÃ OVERRIDE CHỌN AN TOÀN (SAFE)
    if (ov === "SAFE") {
      const el = document.createElement("div");
      el.className = "ps-ban ps-good";
      el.innerHTML =
        `<div class="ps-top"><span class="ps-lamp" style="background:#0a6a3e">👤</span>` +
        `<div><div class="ps-word" style="color:#0a6a3e">PHÁN QUYẾT CỦA BẠN: AN TOÀN · CHỐT CHẶN CUỐI CÙNG</div>` +
        `<div class="ps-say">Bạn đã xác thực tính an toàn của email này sau khi kiểm định cá nhân. Trợ lý PhishShield đã tháo toàn bộ phong tỏa trên các đường link trong thư để bạn tự do, thoải mái làm việc mà không gặp gián đoạn!</div></div></div>` +
        `<div class="ps-foot" style="background:#e4f5eb;border-top:1px solid #a6d9bd">` +
        `<span class="ps-tier local" style="background:#fff;color:#0a6a3e;border-color:#0a6a3e">👤 HUMAN OVERRIDE (ACTIVE)</span>` +
        `<span>Quyết định cá nhân đã ghi nhớ vào hệ thống</span>` +
        `<button class="ps-reset-btn ps-interactive-btn" style="margin-left:auto;background:#fff;border:1px solid #0a6a3e;color:#0a6a3e;border-radius:4px;padding:5px 11px;font-size:12px;font-weight:700">🔄 Khôi phục phán quyết AI gốc</button></div>`;
      
      const resetBtn = el.querySelector(".ps-reset-btn");
      if (resetBtn && t) {
        resetBtn.addEventListener("click", () => {
          setOverride(t.threadId, null);
          paint(r, t, pending);
        });
      }
      return el;
    }

    // TRƯỜNG HỢP 2: NGƯỜI DÙNG ĐÃ OVERRIDE CHỌN ĐỘC HẠI / BÁO CÁO SOC
    if (ov === "DANGER") {
      const el = document.createElement("div");
      el.className = "ps-ban ps-bad";
      el.innerHTML =
        `<div class="ps-top"><span class="ps-lamp" style="background:#bf0f1d">🛡️</span>` +
        `<div><div class="ps-word" style="color:#bf0f1d">PHÁN QUYẾT CỦA BẠN: CHỐT LỪA ĐẢO · ĐÃ BÁO CÁO SOC IT</div>` +
        `<div class="ps-say">Bạn đã chính thức xác định email này là nguy cơ an ninh lừa đảo. Quyết định cảnh giác xuất sắc của bạn đã được ghi nhận vào vòng lặp học tập để tiếp tục nâng cấp mô hình Trợ lý AI (Human-Guided RLHF)!</div></div></div>` +
        `<div class="ps-foot" style="background:#fdecec;border-top:1px solid #f2b7b7">` +
        `<span class="ps-tier" style="background:#bf0f1d;color:#fff;border-color:#bf0f1d">🛡️ SOC USER CONFIRMED</span>` +
        `<span>Đã nạp bằng chứng vào cơ sở bảo mật</span>` +
        `<button class="ps-reset-btn ps-interactive-btn" style="margin-left:auto;background:#fff;border:1px solid #bf0f1d;color:#bf0f1d;border-radius:4px;padding:5px 11px;font-size:12px;font-weight:700">🔄 Khôi phục phán quyết AI gốc</button></div>`;
      
      const resetBtn = el.querySelector(".ps-reset-btn");
      if (resetBtn && t) {
        resetBtn.addEventListener("click", () => {
          setOverride(t.threadId, null);
          paint(r, t, pending);
        });
      }
      return el;
    }

    // TRƯỜNG HỢP 3: HIỂN THỊ PHÁN QUYẾT AI GỐC KÈM CỤM NÚT OVERRIDE
    const v = norm(r.verdict);
    const conf = esc(r.confidence || "?");
    const wait = pending ? `<span class="ps-wait">đang hỏi AI…</span>` : "";
    const draft = r.action_draft || null;

    if (v === "SAFE") {
      const q = document.createElement("div");
      q.className = "ps-quiet";
      
      let draftHtml = "";
      if (draft && draft.message_template) {
        draftHtml = `<div style="margin-top:5px;padding:9px 11px;background:#fff;border:1px solid #a6d9bd;border-radius:5px;font-size:12.5px">` +
          `<div style="font-weight:700;color:#0a6a3e;margin-bottom:4px">${esc(draft.message_title || "💡 Gợi ý thao tác phản hồi an toàn")}</div>` +
          `<div style="font-family:inherit;white-space:pre-wrap;color:#222;margin-bottom:7px;background:#f8faf9;padding:7px 9px;border-radius:4px;border:1px solid #e0eee6">${esc(draft.message_template)}</div>` +
          `<div style="display:flex;align-items:center;gap:9px">` +
          `<button class="ps-copy-btn ps-interactive-btn" style="background:#0a6a3e;color:#fff;border:0;border-radius:4px;padding:6px 12px;font-size:12px;font-weight:600">📋 Sao Chép Bản Nháp</button>` +
          `<button class="ps-ov-danger-btn ps-interactive-btn" style="margin-left:auto;background:transparent;color:#bf0f1d;border:1px solid #f2b7b7;border-radius:4px;padding:5px 10px;font-size:11.5px">🚨 Báo cáo lỗi nghi ngờ (Override)</button>` +
          `</div></div>`;
      }

      q.innerHTML =
        `<div style="display:flex;align-items:center;gap:9px">` +
        `<span style="color:#0a6a3e;font-weight:700">✓</span>` +
        `<span>PhishShield không thấy dấu hiệu bất thường trong thư này.</span>` +
        `<span style="margin-left:auto;font-family:ui-monospace,monospace;font-size:11.5px;color:#0a6a3e">` +
        `độ tin cậy: ${conf} · ${r.tier === "cloud" ? "đã hỏi AI" : "tại chỗ"}</span>` +
        `</div>${draftHtml}`;

      const copyBtn = q.querySelector(".ps-copy-btn");
      if (copyBtn && draft) {
        copyBtn.addEventListener("click", () => {
          navigator.clipboard.writeText(draft.message_template);
          copyBtn.textContent = "✅ Đã Sao Chép Nháp!";
          setTimeout(() => { copyBtn.textContent = "📋 Sao Chép Bản Nháp"; }, 2000);
        });
      }
      const ovDangerBtn = q.querySelector(".ps-ov-danger-btn");
      if (ovDangerBtn && t) {
        ovDangerBtn.addEventListener("click", () => {
          setOverride(t.threadId, "DANGER");
          paint(r, t, false);
        });
      }

      return q;
    }

    const seen = new Set();
    const items = (r.evidence || [])
      .filter((e) => !seen.has(e.text) && seen.add(e.text))
      .map((e, i) => `<li><span class="ps-k">${i + 1}</span><span>${esc(e.text)}</span></li>`)
      .join("");

    let draftSection = "";
    if (draft && draft.message_template) {
      const btnColor = v === "DANGER" ? "#bf0f1d" : "#835500";
      draftSection = `<div style="padding:11px 16px;background:rgba(255,255,255,0.75);border-top:1px solid var(--ps-line)">` +
        `<div style="font-weight:700;font-size:13.5px;color:var(--ps-c);margin-bottom:5px">${esc(draft.message_title || "💡 Bản nháp hành động từ Trợ lý AI")}</div>` +
        `<div style="font-size:13px;color:#11151c;background:#fff;padding:9px 11px;border-radius:5px;border:1px solid var(--ps-line);margin-bottom:8px;white-space:pre-wrap;font-family:inherit;line-height:1.45">${esc(draft.message_template)}</div>` +
        `<button class="ps-copy-btn ps-interactive-btn" style="background:${btnColor};color:#fff;border:0;border-radius:5px;padding:7px 14px;font-size:12.5px;font-weight:600">📋 Sao chép bản nháp gửi cho ${esc(draft.target_recipient || "Đối tác")}</button>` +
        `</div>`;
    }

    // Cụm Nút Phán Quyết Của Người Dùng (Human-in-the-Loop Override Bar)
    const overrideBar = `<div style="padding:10px 16px;background:#f9fbfd;border-top:1px solid var(--ps-line);display:flex;align-items:center;gap:10px;flex-wrap:wrap">` +
      `<span style="font-size:13px;font-weight:700;color:#222">👤 Quyết định cuối cùng thuộc về bạn:</span>` +
      `<button class="ps-ov-safe-btn ps-interactive-btn" style="background:#0a6a3e;color:#fff;border:0;border-radius:5px;padding:6px 13px;font-size:12.5px;font-weight:600">🟢 Tôi đã xác minh: Email này An toàn</button>` +
      `<button class="ps-ov-danger-btn ps-interactive-btn" style="background:#11151c;color:#fff;border:0;border-radius:5px;padding:6px 13px;font-size:12.5px;font-weight:600">🔴 Chốt là Lừa đảo (Báo cáo SOC)</button>` +
      `</div>`;

    const el = document.createElement("div");
    el.className = `ps-ban ${LEVEL[v]}`;
    el.innerHTML =
      `<div class="ps-top"><span class="ps-lamp">${LAMP[v]}</span>` +
      `<div><div class="ps-word">${WORD[v]} · độ tin cậy ${conf}${wait}</div>` +
      `<div class="ps-say">${esc(r.recommendation || "")}</div></div></div>` +
      (items ? `<ul class="ps-ev">${items}</ul>` : "") +
      draftSection +
      overrideBar +
      `<div class="ps-foot"><span class="ps-tier ${r.tier}">` +
      `${r.tier === "cloud" ? "CÓ GỌI AI" : "TẠI CHỖ"}</span>` +
      (r.cached ? `<span class="ps-cached">đã lưu · không gọi lại API</span>` : "") +
      `<span>${esc(r.analysis_source || "")}</span>` +
      `<span style="margin-left:auto;font-weight:600">Human-in-the-Loop Copilot</span></div>`;

    const copyBtn = el.querySelector(".ps-copy-btn");
    if (copyBtn && draft) {
      copyBtn.addEventListener("click", () => {
        navigator.clipboard.writeText(draft.message_template);
        copyBtn.textContent = "✅ Đã Sao Chép Nháp!";
        setTimeout(() => { copyBtn.textContent = `📋 Sao chép bản nháp gửi cho ${draft.target_recipient || "Đối tác"}`; }, 2000);
      });
    }

    const ovSafeBtn = el.querySelector(".ps-ov-safe-btn");
    if (ovSafeBtn && t) {
      ovSafeBtn.addEventListener("click", () => {
        setOverride(t.threadId, "SAFE");
        paint(r, t, false);
      });
    }

    const ovDangerBtn = el.querySelector(".ps-ov-danger-btn");
    if (ovDangerBtn && t) {
      ovDangerBtn.addEventListener("click", () => {
        setOverride(t.threadId, "DANGER");
        paint(r, t, false);
      });
    }

    return el;
  }

  function gate(href) {
    const g = document.createElement("div");
    g.className = "ps-gate";
    g.innerHTML =
      `<div class="ps-card" role="dialog" aria-modal="true">` +
      `<h2>Khoan đã — liên kết này bị đánh dấu nguy hiểm</h2>` +
      `<p>PhishShield cho rằng trang đích có chứa mồi nhử hoặc rủi ro an ninh cao.</p>` +
      `<div class="ps-target">${esc(href)}</div><div class="ps-acts">` +
      `<button class="ps-safe-btn ps-interactive-btn">Quay lại, đừng mở</button>` +
      `<button class="ps-risky-btn ps-interactive-btn">Tôi hiểu rủi ro, vẫn mở</button></div></div>`;
    const close = () => g.remove();
    g.querySelector(".ps-safe-btn").addEventListener("click", close);
    g.querySelector(".ps-risky-btn").addEventListener("click", close);
    g.addEventListener("click", (e) => { if (e.target === g) close(); });
    document.body.appendChild(g);
    g.querySelector(".ps-safe-btn").focus();
  }

  const devCache = new Map();
  const devInflight = new Map();
  const DEV_TTL = 15 * 60 * 1000;

  async function ask(text, path) {
    if (!IS_EXT) {
      if (path === "/analyze") {
        const hit = devCache.get(text);
        if (hit && Date.now() - hit.at < DEV_TTL) {
          return { ok: true, data: { ...hit.data, cached: true } };
        }
        const pending = devInflight.get(text);
        if (pending) return { ok: true, data: { ...(await pending), cached: true } };
      }

      const call = fetch("http://127.0.0.1:8777" + path, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      }).then((res) => res.json());

      if (path === "/analyze") {
        devInflight.set(text, call);
        call.finally(() => devInflight.delete(text));
      }

      const data = await call;
      if (path === "/analyze") devCache.set(text, { data, at: Date.now() });
      return { ok: true, data: { ...data, cached: false } };
    }
    return chrome.runtime.sendMessage({ type: "PS_ANALYZE", text, path });
  }

  function composeForEngine(t) {
    const lines = [`Chủ đề: ${t.subject}`, `Người gửi: ${t.fromName} <${t.fromAddress}>`];
    const replyTo = (t.rawHeaders || "").match(/^Reply-?To:[ \t]*(.+)$/im)?.[1];
    if (replyTo) lines.push(`Reply-To: ${replyTo.trim()}`);
    return lines.join("\n") + "\n\n" + t.bodyText;
  }

  let generation = 0;

  const OFFLINE = (err) => ({
    verdict: "DOUBT", tier: "local", confidence: "THẤP", evidence: [],
    recommendation: "Không kết nối được engine PhishShield. Chưa kiểm tra được thư này — " +
                    "đừng bấm liên kết cho tới khi kiểm tra lại.",
    analysis_source: "BRIDGE UNAVAILABLE: " + (err || "unknown"),
  });

  function paint(r, t, pending) {
    A.mountBanner(buildBanner(r, pending, t));
    
    const ov = t ? getOverrides()[t.threadId] : null;
    const effectiveVerdict = ov === "SAFE" ? "SAFE" : (ov === "DANGER" ? "DANGER" : r.verdict);

    // Nếu phán quyết hiện tại (sau Override) là AN TOÀN -> Tháo toàn bộ phong tỏa đỏ trên link!
    if (effectiveVerdict === "SAFE" || effectiveVerdict === "DOUBT") {
      for (const l of t.links) {
        l.el.classList.remove("ps-danger-link");
      }
      return;
    }

    // Nếu phán quyết là DANGER -> Kích hoạt khóa khiên bảo vệ trên các link
    for (const l of t.links) {
      l.el.classList.add("ps-danger-link");
      if (l.el.dataset.psGated) continue;
      l.el.dataset.psGated = "1";
      l.el.addEventListener("click", (e) => {
        const currentOv = getOverrides()[t.threadId];
        if (currentOv === "SAFE") return; // Nới lỏng hoàn toàn nếu đã xác minh An toàn!
        e.preventDefault();
        e.stopPropagation();
        gate(l.href);
      });
    }
  }

  async function onThread(t) {
    const mine = ++generation;
    const threadId = t.threadId;

    const stillCurrent = () =>
      mine === generation && A.readThread()?.threadId === threadId;

    const text = composeForEngine(t);

    let quick;
    try { quick = await ask(text, "/scan"); } catch (err) { quick = { ok: false, error: String(err) }; }
    if (!stillCurrent()) return;

    const first = quick?.ok ? quick.data : OFFLINE(quick?.error);
    paint(first, t, !!first.pending_llm);

    if (!first.pending_llm) return;

    await new Promise((r) => setTimeout(r, 450));
    if (!stillCurrent()) return;

    let full;
    try { full = await ask(text, "/analyze"); } catch (err) { full = { ok: false, error: String(err) }; }
    if (!stillCurrent()) return;

    paint(full?.ok ? full.data : OFFLINE(full?.error), t, false);
  }

  A.onThreadChange(onThread);
})();
