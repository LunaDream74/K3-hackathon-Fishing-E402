import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict, Any, List
from urllib.parse import urlparse

# Reconfigure stdout for UTF-8 compatibility on Windows terminals
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Cấu hình đường dẫn Root và Codebase
ROOT = Path(__file__).resolve().parent.parent
CODEBASE_DIR = ROOT / "codebase"
if str(CODEBASE_DIR) not in sys.path:
    sys.path.insert(0, str(CODEBASE_DIR))

# Import các thành phần từ codebase
try:
    from env_loader import get_config
    from tools.url_scanner import scan_text_and_urls
    from agent import PhishingAgent
    CODEBASE_AVAILABLE = True
except Exception as e:
    CODEBASE_AVAILABLE = False
    IMPORT_ERROR = str(e)

DATA_PATH = ROOT / "eval" / "golden_set.json"
RUNS_DIR = ROOT / "eval" / "runs"
DEFAULT_OUTPUT_PATH = RUNS_DIR / "latest_run.json"


def format_text_input(case: Dict[str, Any]) -> str:
    """Tạo chuỗi đầu vào email chuẩn cho Agent từ thông tin case."""
    subject = case.get("email_subject", "").strip()
    body = case.get("email_body", "").strip()
    url = case.get("url", "").strip()
    
    parts = []
    if subject:
        parts.append(f"Chủ đề: {subject}")
    if body:
        parts.append(f"Nội dung: {body}")
    if url:
        parts.append(f"Liên kết đính kèm: {url}")
        
    return "\n".join(parts)


def rule_fallback_predict(case: Dict[str, Any]) -> Dict[str, Any]:
    """Dự đoán dựa hoàn toàn vào Rule Engine tĩnh (url_scanner) cho chế độ offline/mock."""
    text_input = format_text_input(case)
    scan_res = scan_text_and_urls(text_input)
    
    if not scan_res.get("needs_llm_call", True):
        det = scan_res["deterministic_result"]
        return {
            "risk_level": det.get("risk_level", "SAFE"),
            "risk_score": det.get("risk_score", 0),
            "suspicious_elements": det.get("suspicious_elements", []),
            "recommendation": det.get("recommendation", ""),
            "analysis_source": det.get("analysis_source", "RULE_ENGINE")
        }
    
    # Ca cần LLM nhưng đang chạy offline rule mode: heuristic đoán nhẹ
    url = case.get("url", "").lower()
    text = text_input.lower()
    
    if any(shortener in url for shortener in ["bit.ly", "tinyurl", "t.co"]):
        risk = "DANGER"
        score = 85
    elif any(kw in text for kw in ["mật khẩu", "password", "xác thực", "verify", "khẩn", "urgent"]):
        risk = "DANGER" if any(ext in url for ext in [".tk", ".xyz", ".top", ".info"]) else "WARNING"
        score = 75 if risk == "DANGER" else 45
    else:
        risk = "SAFE"
        score = 20
        
    return {
        "risk_level": risk,
        "risk_score": score,
        "suspicious_elements": ["Rule fallback estimate (No LLM called)"],
        "recommendation": "Cần kiểm tra kỹ hơn bằng LLM Reasoning.",
        "analysis_source": "RULE_FALLBACK_ESTIMATE"
    }


def map_risk_to_prediction(risk_level: str) -> tuple[str, str]:
    """
    Ánh xạ risk_level ("SAFE", "WARNING", "DANGER") thành (prediction, action).

    Sản phẩm có ĐÚNG BA phán quyết — An toàn / Nghi vấn / Nguy hiểm — nên bảng chấm
    điểm cũng phải có ba ô. Trước đây WARNING bị quy về ("safe", "allow"): hệ thống
    nói "nghi vấn" mà bảng điểm ghi là "đã cho qua an toàn".

    Hai hệ quả:
      1. Recall bị báo thấp hơn thực tế (61.5% thay vì 92.3% trên cùng dữ liệu).
      2. "allow" cho một email hệ thống đang không chắc chính là vi phạm hard-spot ④
         ngay trong cách chấm điểm.

    WARNING giờ là ô riêng, hành động "warn" — người dùng được cảnh báo, không bị
    chặn, và cũng không bị bảo là an toàn.
    """
    risk = str(risk_level).upper()
    if risk == "DANGER":
        return "phishing", "block"
    elif risk == "WARNING":
        return "suspicious", "warn"
    else:
        return "safe", "allow"


def run_evaluation(cases: List[Dict[str, Any]], mode: str = "live", model_name: str = "gpt-4o-mini") -> Dict[str, Any]:
    agent = None
    if mode == "live":
        if not CODEBASE_AVAILABLE:
            raise RuntimeError(f"Không thể import codebase module: {IMPORT_ERROR}")
        try:
            agent = PhishingAgent(model_name=model_name)
        except Exception as err:
            print(f"[Warning] Không thể khởi tạo PhishingAgent với LLM ({err}). Chuyển sang chế độ rule-based.")
            mode = "rule"

    results = []
    tp = fp = tn = fn = 0
    friction = 0  # thư sạch bị gán WARNING — gây phiền, nhưng không phải báo nhầm
    rule_hits = 0
    llm_calls = 0
    start_time = time.time()
    
    hard_spot_stats = {}

    for index, case in enumerate(cases, 1):
        text_input = format_text_input(case)
        expected_label = case["expected_label"]
        category = case.get("hard_spot_category", "normal")
        
        if category not in hard_spot_stats:
            hard_spot_stats[category] = {"total": 0, "correct": 0, "tp": 0, "fp": 0, "tn": 0, "fn": 0}
        hard_spot_stats[category]["total"] += 1

        t0 = time.time()
        if mode == "live" and agent:
            try:
                agent_res = agent.analyze_email(text_input)
            except Exception as e:
                print(f"[Error Case {case['id']}] Lỗi khi gọi Agent: {e}")
                agent_res = rule_fallback_predict(case)
        else:
            agent_res = rule_fallback_predict(case)
        latency_ms = round((time.time() - t0) * 1000, 2)

        risk_level = agent_res.get("risk_level", "SAFE")
        source = agent_res.get("analysis_source", "UNKNOWN")
        
        if "RULE" in source:
            rule_hits += 1
        else:
            llm_calls += 1

        pred_label, pred_action = map_risk_to_prediction(risk_level)

        # Chấm điểm ba lớp, theo đúng mức thiệt hại thật của từng loại sai:
        #
        #   lừa đảo -> DANGER   bắt chắc          (tp)
        #   lừa đảo -> WARNING  vẫn được cảnh báo (tp — người dùng được bảo vệ)
        #   lừa đảo -> SAFE     BỎ SÓT            (fn — nguy hiểm nhất)
        #   sạch    -> SAFE     cho qua đúng      (tn)
        #   sạch    -> WARNING  gây phiền         (friction — chưa chắc, không chặn)
        #   sạch    -> DANGER   BÁO NHẦM          (fp — tốn kém nhất phía người dùng)
        #
        # "friction" cố tình KHÔNG gộp vào fp: nói "nghi vấn" về một thư sạch không
        # giống với việc gán nó là nguy hiểm. Nhưng cũng không tính là đúng —
        # nó vẫn là chi phí. Cách tính này giữ accuracy ở mức dè dặt.
        if expected_label == "phishing":
            if pred_label == "phishing":
                tp += 1; hard_spot_stats[category]["tp"] += 1
                outcome = "correct"
            elif pred_label == "suspicious":
                tp += 1; hard_spot_stats[category]["tp"] += 1
                outcome = "correct_warned"
            else:
                fn += 1; hard_spot_stats[category]["fn"] += 1
                outcome = "miss"
        else:
            if pred_label == "safe":
                tn += 1; hard_spot_stats[category]["tn"] += 1
                outcome = "correct"
            elif pred_label == "suspicious":
                friction += 1
                outcome = "friction"
            else:
                fp += 1; hard_spot_stats[category]["fp"] += 1
                outcome = "false_alarm"

        if outcome in ("correct", "correct_warned"):
            hard_spot_stats[category]["correct"] += 1

        results.append({
            "id": case["id"],
            "scenario": case["scenario"],
            "hard_spot_category": category,
            "url": case.get("url", ""),
            "expected_label": expected_label,
            "expected_action": case.get("expected_action", "allow"),
            "predicted_risk_level": risk_level,
            "predicted_label": pred_label,
            "predicted_action": pred_action,
            "outcome": outcome,
            "analysis_source": source,
            "latency_ms": latency_ms,
            "risk_score": agent_res.get("risk_score", 0),
            "recommendation": agent_res.get("recommendation", ""),
            "suspicious_elements": agent_res.get("suspicious_elements", [])
        })

    total = len(cases)
    elapsed_sec = round(time.time() - start_time, 2)
    # accuracy dè dặt: "friction" KHÔNG được tính là đúng.
    accuracy = (tp + tn) / total if total > 0 else 0.0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

    # Mẫu số là TOÀN BỘ thư sạch (kể cả thư bị gán WARNING), nên fp_rate vẫn
    # là "tỷ lệ thư sạch bị gán NGUY HIỂM" — đúng loại sai mà quality bar nhắm tới.
    total_safe = fp + tn + friction
    fp_rate = fp / total_safe if total_safe > 0 else 0.0
    friction_rate = friction / total_safe if total_safe > 0 else 0.0
    fn_rate = fn / (tp + fn) if (tp + fn) > 0 else 0.0

    category_summary = {}
    for cat, stat in hard_spot_stats.items():
        cat_tot = stat["total"]
        cat_corr = stat["correct"]
        cat_acc = round(cat_corr / cat_tot, 3) if cat_tot > 0 else 0.0
        category_summary[cat] = {
            "total_cases": cat_tot,
            "correct_cases": cat_corr,
            "accuracy": cat_acc,
            "tp": stat["tp"],
            "fp": stat["fp"],
            "tn": stat["tn"],
            "fn": stat["fn"]
        }

    return {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "eval_mode": mode,
        "total_cases": total,
        "execution_time_seconds": elapsed_sec,
        "metrics": {
            "accuracy": round(accuracy, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4),
            "fp_rate": round(fp_rate, 4),
            "fn_rate": round(fn_rate, 4),
            "friction_rate": round(friction_rate, 4)
        },
        "confusion_matrix": {
            "tp": tp,
            "fp": fp,
            "tn": tn,
            "fn": fn,
            "friction": friction
        },
        "hybrid_architecture_stats": {
            "rule_based_hits": rule_hits,
            "llm_reasoning_calls": llm_calls,
            "rule_hit_rate_pct": round((rule_hits / total) * 100, 2) if total > 0 else 0.0
        },
        "hard_spot_breakdown": category_summary,
        "results": results
    }


def print_cli_summary(report: Dict[str, Any]) -> None:
    """In kết quả đánh giá theo giao diện bảng trên Terminal."""
    m = report["metrics"]
    cm = report["confusion_matrix"]
    hb = report["hybrid_architecture_stats"]
    
    print("\n" + "=" * 75)
    print("[EVAL REPORT] BAO CAO DANH GIA HE THONG PHISHSHIELD AI AGENT")
    print("=" * 75)
    print(f"[*] Che do: {report['eval_mode'].upper()} | Thoi gian: {report['timestamp']} | Tong cases: {report['total_cases']}")
    print("-" * 75)
    print("[METRICS] MUC TIEU & CHI SO CHAT LUONG VAN HANH:")
    print(f"   * Accuracy  (Do chinh xac chung) : {m['accuracy'] * 100:.1f}%")
    print(f"   * Precision (Do chuan xac)      : {m['precision'] * 100:.1f}%")
    print(f"   * Recall    (Do bao phu Phishing): {m['recall'] * 100:.1f}%  (Muc tieu: >= 95.0%)")
    print(f"   * F1-Score  (Dung hoa F1)        : {m['f1_score'] * 100:.1f}%")
    print(f"   * False Positive Rate (Bao nham) : {m['fp_rate'] * 100:.1f}%  (Muc tieu: < 5.0%)")
    print(f"   * Friction Rate (thu sach -> WARNING): {m.get('friction_rate', 0) * 100:.1f}%  (canh bao, KHONG chan)")
    print(f"   * False Negative Rate (Bo sot)  : {m['fn_rate'] * 100:.1f}%  (Rui ro cao nhat!)")
    print("-" * 75)
    print(f"[CONFUSION MATRIX] TP={cm['tp']} | TN={cm['tn']} | FP={cm['fp']} (Bao nham) | FN={cm['fn']} (Bo sot) | Friction={cm.get('friction', 0)} (thu sach -> WARNING)")
    print("-" * 75)
    print("[HYBRID STATS] HIEU QUA MO HINH LAI (RULE vs LLM):")
    print(f"   * Rule-based Engine xu ly      : {hb['rule_based_hits']}/{report['total_cases']} cases ({hb['rule_hit_rate_pct']}%) -> TIET KIEM LLM TOKEN")
    print(f"   * LLM Reasoning xu ly          : {hb['llm_reasoning_calls']}/{report['total_cases']} cases")
    print("-" * 75)
    print("[HARD SPOT BREAKDOWN] DANH GIA THEO 4 LOP CHO KHO:")
    print(f"   {'Hard Spot Category':<35} | {'Cases':<6} | {'Dung':<6} | {'Accuracy':<10}")
    print("   " + "-" * 65)
    for cat, stat in report["hard_spot_breakdown"].items():
        print(f"   {cat:<35} | {stat['total_cases']:<6} | {stat['correct_cases']:<6} | {stat['accuracy'] * 100:>6.1f}%")
    print("=" * 75 + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Chuong trinh kiem thu Eval cho PhishShield AI Agent")
    parser.add_argument("--mode", choices=["live", "rule"], default="live", help="Che do danh gia (live: chay LLM that, rule: chay quy tac tinh offline)")
    parser.add_argument("--model", default="gpt-4o-mini", help="Mo hinh LLM su dung khi o che do live")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH), help="Duong dan file ket qua xuat JSON")
    args = parser.parse_args()

    if not DATA_PATH.exists():
        print(f"[Error] Khong tim thay dataset Golden Set tai {DATA_PATH}")
        sys.exit(1)

    cases = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    print(f"[EVAL] Bat dau danh gia PhishShield AI Agent voi dataset {len(cases)} cases (Mode: {args.mode})...")

    report = run_evaluation(cases, mode=args.mode, model_name=args.model)
    
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print_cli_summary(report)
    print(f"[INFO] Ket qua chi tiet da duoc luu tai: {output_path}")


if __name__ == "__main__":
    main()
