/* ============================================================================
   KIỂM TRA HỢP ĐỒNG DOM — dán nguyên file này vào DevTools Console
   khi đang mở http://localhost:8931/inbox.html

   Dùng để chứng minh hợp đồng đọc được TRƯỚC khi viết tiện ích.
   Không phụ thuộc gì vào PhishShield. Bản sao inline của adapter tham chiếu
   (Console không import module được).
   ============================================================================ */
(() => {
  const need = ["subject", "from-name", "from-address", "body"];
  const want = ["date", "raw-headers"];

  const host = document.body?.dataset.psHost;
  const ver = document.body?.dataset.psContract;
  console.log("%cHỢP ĐỒNG DOM PHISHSHIELD", "font-weight:700;font-size:13px");
  console.log("host:", host ?? "(thiếu)", "· contract v" + (ver ?? "?"));

  const root = document.querySelector("[data-ps-thread]");
  if (!root) {
    console.error("✗ Không thấy [data-ps-thread] — chưa mở thư nào?");
    return;
  }

  let ok = true;
  const read = (f) => {
    const el = root.querySelector(`[data-ps-field="${f}"]`);
    return el ? el.textContent.trim() : null;
  };

  console.log("threadId:", root.getAttribute("data-ps-thread-id") || "(thiếu)");

  for (const f of need) {
    const v = read(f);
    if (v === null || v === "") { ok = false; console.error(`✗ THIẾU (bắt buộc): ${f}`); }
    else console.log(`✓ ${f}:`, v.length > 70 ? v.slice(0, 70) + "…" : v);
  }
  for (const f of want) {
    const v = read(f);
    if (v === null || v === "") console.warn(`○ trống (tuỳ chọn): ${f}`);
    else console.log(`✓ ${f}:`, v.split("\n")[0] + (v.includes("\n") ? " …" : ""));
  }

  const slot = root.querySelector('[data-ps-slot="banner"]');
  if (!slot) { ok = false; console.error("✗ THIẾU chỗ chèn banner [data-ps-slot=\"banner\"]"); }
  else console.log("✓ chỗ chèn banner: sẵn sàng");

  const bodyEl = root.querySelector('[data-ps-field="body"]');
  const links = bodyEl ? [...bodyEl.querySelectorAll("a[href]")] : [];
  console.log(`✓ liên kết trong thân thư: ${links.length}`);
  links.forEach((a, i) => console.log(`   ${i + 1}. ${a.getAttribute("href")}`));

  // Phần dễ sai nhất: đổi thư KHÔNG tải lại trang.
  let last = root.getAttribute("data-ps-thread-id");
  const mo = new MutationObserver(() => {
    const el = document.querySelector("[data-ps-thread]");
    const id = el?.getAttribute("data-ps-thread-id") ?? null;
    if (id && id !== last) {
      last = id;
      console.log("%c↻ đã mở thư khác → " + id + " (không tải lại trang)", "color:#1f34c4");
    }
  });
  mo.observe(document.body, { childList: true, subtree: true });

  console.log(
    ok ? "%c✓ HỢP ĐỒNG ĐẠT — bấm sang thư khác để xem MutationObserver báo."
       : "%c✗ HỢP ĐỒNG CHƯA ĐẠT — xem các dòng lỗi ở trên.",
    ok ? "color:#0a6a3e;font-weight:700" : "color:#bf0f1d;font-weight:700"
  );
  console.log("Dừng theo dõi: mo.disconnect() — biến `mo` đã có sẵn.");
  window.mo = mo;
})();
