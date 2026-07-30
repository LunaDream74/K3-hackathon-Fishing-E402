"""
Cầu nối HTTP giữa tiện ích Chrome và engine v1.

VÌ SAO CÓ FILE NÀY: tiện ích chạy bằng JavaScript, engine v1 viết bằng Python.
Cách rẻ nhất để tiện ích dùng ĐÚNG code của v1 (thay vì chép lại logic sang JS
rồi để hai bản trôi lệch nhau) là bọc nó sau một endpoint HTTP chạy tại localhost.

File này KHÔNG chứa logic phát hiện. Nó chỉ gọi lại:
    tools.url_scanner.scan_text_and_urls   (tầng luật tĩnh)
    agent.PhishingAgent                    (tầng LLM, chỉ khi có API key)
và dịch kết quả sang đúng hợp đồng mà giao diện tiện ích cần.

Chỉ dùng thư viện chuẩn — không thêm dependency nào.

Chạy:
    .venv/Scripts/python.exe codebase/bridge.py
    # POST http://127.0.0.1:8777/analyze  {"text": "..."}
"""

import json
import sys
import traceback
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

CODEBASE_DIR = Path(__file__).resolve().parent
if str(CODEBASE_DIR) not in sys.path:
    sys.path.insert(0, str(CODEBASE_DIR))

from tools.url_scanner import scan_text_and_urls  # noqa: E402

# Tầng LLM là tuỳ chọn: không có key thì bridge vẫn chạy, chỉ còn tầng luật tĩnh.
try:
    from env_loader import get_config
    _HAS_KEY = bool(get_config().get("OPENAI_API_KEY"))
except Exception:
    _HAS_KEY = False

_agent = None


def _get_agent():
    """Khởi tạo PhishingAgent một lần, chỉ khi thật sự cần gọi LLM."""
    global _agent
    if _agent is None:
        from agent import PhishingAgent
        _agent = PhishingAgent(model_name="gpt-4o-mini")
    return _agent


# Chỉ có ĐÚNG BA phán quyết. Người dùng là người ra quyết định cuối cùng, nên
# sản phẩm chỉ nói "an toàn / nghi vấn / nguy hiểm" kèm ĐỘ TIN CẬY, không tự hành động.
#
# Mọi trường hợp không kết luận được (thiếu dữ liệu, engine lỗi, nhãn lạ) đều rơi vào
# NGHI VẤN với độ tin cậy THẤP — không bao giờ được rơi xuống AN TOÀN. Đó là hard-spot ④.
_VERDICT = {"SAFE": "SAFE", "WARNING": "DOUBT", "DANGER": "DANGER"}


def _to_contract(raw: dict, tier: str) -> dict:
    """Dịch đầu ra của engine v1 sang hợp đồng giao diện tiện ích."""
    level = str(raw.get("risk_level", "")).upper()
    # Nhãn lạ -> NGHI VẤN, không phải AN TOÀN.
    verdict = _VERDICT.get(level, "DOUBT")
    score = raw.get("risk_score")

    elements = raw.get("suspicious_elements") or []
    evidence = [{"tone": "bad" if verdict == "DANGER" else "warn", "text": str(e)} for e in elements]
    if not evidence:
        evidence = [{
            "tone": "good" if verdict == "SAFE" else "info",
            "text": raw.get("recommendation") or "Không có dấu hiệu nào được ghi nhận.",
        }]

    # Guardrail an toàn-bi-quan: thiếu tầng LLM thì không được khẳng định "an toàn"
    # với độ tin cậy cao. Xem hard-spot 4.
    if verdict == "SAFE" and tier == "local" and not _HAS_KEY:
        confidence = "TRUNG BÌNH"
    elif verdict == "SAFE":
        confidence = "CAO"
    else:
        confidence = "CAO" if tier == "cloud" else "TRUNG BÌNH"

    return {
        "engine": "v1",
        "tier": tier,
        "verdict": verdict,
        "risk_score": score,
        "confidence": confidence,
        "evidence": evidence,
        "recommendation": raw.get("recommendation", ""),
        "analysis_source": raw.get("analysis_source", ""),
        "extracted_urls": raw.get("extracted_urls", []),
    }


def analyze(text: str) -> dict:
    """Chạy đúng luồng hai tầng của v1."""
    scan = scan_text_and_urls(text)

    if not scan.get("needs_llm_call", True):
        # Tầng 1 đã đủ kết luận — không có byte nào rời khỏi máy.
        return _to_contract(scan["deterministic_result"], tier="local")

    if not _HAS_KEY:
        # Cần LLM nhưng không có key: NGHI VẤN + độ tin cậy THẤP.
        # Tuyệt đối không hạ xuống "an toàn".
        return {
            "engine": "v1",
            "tier": "local",
            "verdict": "DOUBT",
            "risk_score": None,
            "confidence": "THẤP",
            "evidence": [{"tone": "info", "text": r} for a in scan.get("url_analyses", [])
                         for r in a.get("reasons", [])] or
                        [{"tone": "info", "text": "Có tên miền lạ cần thẩm định sâu hơn."}],
            "recommendation": "Chưa đủ căn cứ để kết luận: tầng suy luận AI chưa được bật "
                              "(thiếu OPENAI_API_KEY). Đừng bấm liên kết cho tới khi kiểm chứng được.",
            "analysis_source": "RULE_ENGINE (LLM unavailable — no API key)",
            "extracted_urls": scan.get("extracted_urls", []),
        }

    return _to_contract(_get_agent().analyze_email(text), tier="cloud")


class Handler(BaseHTTPRequestHandler):
    def _cors(self):
        # Tiện ích gọi từ origin của trang hộp thư, nên cần CORS.
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        if self.path != "/health":
            self.send_error(404)
            return
        self._json(200, {"ok": True, "engine": "v1", "llm_enabled": _HAS_KEY})

    def do_POST(self):
        if self.path != "/analyze":
            self.send_error(404)
            return
        try:
            n = int(self.headers.get("Content-Length") or 0)
            payload = json.loads(self.rfile.read(n) or b"{}")
            text = str(payload.get("text", ""))
            if not text.strip():
                self._json(400, {"error": "thiếu trường 'text'"})
                return
            self._json(200, analyze(text))
        except Exception as exc:
            traceback.print_exc()
            self._json(500, {"error": str(exc)})

    def _json(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self._cors()
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        sys.stderr.write("[bridge] " + (fmt % args) + "\n")


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8777
    print(f"[bridge] engine=v1  llm_enabled={_HAS_KEY}  http://127.0.0.1:{port}")
    if not _HAS_KEY:
        print("[bridge] Chưa có OPENAI_API_KEY — chỉ chạy tầng luật tĩnh (tier 1).")
    HTTPServer(("127.0.0.1", port), Handler).serve_forever()
