"""
Cầu nối HTTP giữa tiện ích Chrome và engine phát hiện (hiện tại: v2).

VÌ SAO CÓ FILE NÀY: tiện ích chạy bằng JavaScript, engine viết bằng Python.
Cách rẻ nhất để tiện ích dùng ĐÚNG code của engine (thay vì chép lại logic sang JS
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

# Nhãn phiên bản engine mà bridge đang bọc. Đây là hằng số thủ công — nếu
# codebase/tools/ được nâng cấp thì SỬA Ở ĐÂY, đừng để /health báo sai phiên bản.
ENGINE = "v2"


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
    """Dịch đầu ra của engine sang hợp đồng giao diện tiện ích."""
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

    # v2 tự chấm độ tin cậy (confidence_level / confidence_score) — dùng của engine
    # thay vì tự suy đoán, vì engine biết nó dựa trên bằng chứng nào.
    # v1 không có trường này, nên vẫn giữ đường suy đoán cũ làm dự phòng.
    _LEVEL = {"HIGH": "CAO", "MEDIUM": "TRUNG BÌNH", "LOW": "THẤP"}
    engine_conf = _LEVEL.get(str(raw.get("confidence_level", "")).upper())

    if engine_conf:
        confidence = engine_conf
    elif verdict == "SAFE":
        confidence = "CAO"
    else:
        confidence = "CAO" if tier == "cloud" else "TRUNG BÌNH"

    # Guardrail an toàn-bi-quan: chưa có tầng LLM thì không được khẳng định
    # "an toàn" với độ tin cậy CAO, kể cả khi engine tự tin. Xem hard-spot ④.
    if verdict == "SAFE" and tier == "local" and not _HAS_KEY and confidence == "CAO":
        confidence = "TRUNG BÌNH"

    return {
        "engine": ENGINE,
        "tier": tier,
        "verdict": verdict,
        "risk_score": score,
        "confidence": confidence,
        "evidence": evidence,
        "recommendation": raw.get("recommendation", ""),
        "analysis_source": raw.get("analysis_source", ""),
        "extracted_urls": raw.get("extracted_urls", []),
        "action_draft": raw.get("action_draft", {
            "draft_type": "REPLY_ACK" if verdict == "SAFE" else ("INCIDENT_REPORT" if verdict == "DANGER" else "VERIFICATION"),
            "target_recipient": "Phòng Ban Hỗ Trợ / Đối Tác",
            "message_title": "💡 Gợi ý thao tác phản hồi nhanh cho email này",
            "message_template": "Cảm ơn bạn, mình đã tiếp nhận và sẽ kiểm tra phản hồi sớm nhé!"
        }),
    }


def scan_only(text: str) -> dict:
    """
    CHỈ chạy tầng luật tĩnh. Không bao giờ gọi LLM, nên trả về gần như tức thì.

    Giao diện gọi endpoint này trước để có câu trả lời ngay, rồi mới nâng cấp
    bằng /analyze nếu cần. Gọi LLM mất vài giây — trong lúc đó người dùng đang
    đọc thư mà không có cảnh báo nào, nên phải nói được điều gì đó ngay lập tức.

    `pending_llm = True` nghĩa là: đây chưa phải kết luận cuối cùng.
    """
    scan = scan_text_and_urls(text)

    if not scan.get("needs_llm_call", True):
        out = _to_contract(scan["deterministic_result"], tier="local")
        out["pending_llm"] = False
        return out

    # Chưa kết luận được bằng luật: NGHI VẤN + THẤP, kèm những gì tầng 1 đã thấy.
    # Tuyệt đối không trả AN TOÀN ở đây.
    reasons = [r for a in scan.get("url_analyses", []) for r in a.get("reasons", [])]
    return {
        "engine": ENGINE,
        "tier": "local",
        "verdict": "DOUBT",
        "risk_score": None,
        "confidence": "THẤP",
        "evidence": [{"tone": "info", "text": r} for r in dict.fromkeys(reasons)]
                    or [{"tone": "info", "text": "Có tên miền lạ cần thẩm định sâu hơn."}],
        "recommendation": "Đang kiểm tra kỹ hơn. Khoan bấm liên kết nào cho tới khi có kết luận.",
        "analysis_source": "RULE_ENGINE (chờ tầng AI)",
        "extracted_urls": scan.get("extracted_urls", []),
        "action_draft": {
            "draft_type": "VERIFICATION",
            "target_recipient": "Bộ phận Hỗ Trợ Kỹ Thuật",
            "message_title": "💡 Gợi ý thao tác: Copy tin nhắn hỏi kiểm chứng liên kết chưa xác thực",
            "message_template": "Chào các bạn, mình vừa nhận được email có mang liên kết bên ngoài chưa nằm trong danh sách kiểm nghiệm chính thức. Cho mình hỏi bên mình có đang triển khai công việc qua trang web này không ạ?"
        },
        "pending_llm": _HAS_KEY,
    }


def analyze(text: str) -> dict:
    """Chạy đúng luồng hai tầng của engine."""
    scan = scan_text_and_urls(text)

    if not scan.get("needs_llm_call", True):
        # Tầng 1 đã đủ kết luận — không có byte nào rời khỏi máy.
        return _to_contract(scan["deterministic_result"], tier="local")

    if not _HAS_KEY:
        # Cần LLM nhưng không có key: NGHI VẤN + độ tin cậy THẤP.
        # Tuyệt đối không hạ xuống "an toàn".
        return {
            "engine": ENGINE,
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
            "action_draft": {
                "draft_type": "VERIFICATION",
                "target_recipient": "Phòng IT Helpdesk",
                "message_title": "💡 Gợi ý thao tác: Copy tin nhắn hỏi xác minh với IT",
                "message_template": "Chào đội IT, mình thấy trong thư có đường link lạ bên ngoài nhưng phần mềm chưa kết nối được máy chủ suy luận AI. Nhờ anh em kỹ thuật kiểm tra giúp tính an toàn của email này nhé!"
            },
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
        self._json(200, {"ok": True, "engine": ENGINE, "llm_enabled": _HAS_KEY})

    def do_POST(self):
        if self.path not in ("/analyze", "/scan"):
            self.send_error(404)
            return
        try:
            n = int(self.headers.get("Content-Length") or 0)
            payload = json.loads(self.rfile.read(n) or b"{}")
            text = str(payload.get("text", ""))
            if not text.strip():
                self._json(400, {"error": "thiếu trường 'text'"})
                return
            self._json(200, scan_only(text) if self.path == "/scan" else analyze(text))
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
    print(f"[bridge] engine={ENGINE}  llm_enabled={_HAS_KEY}  http://127.0.0.1:{port}")
    if not _HAS_KEY:
        print("[bridge] Chưa có OPENAI_API_KEY — chỉ chạy tầng luật tĩnh (tier 1).")
    HTTPServer(("127.0.0.1", port), Handler).serve_forever()
