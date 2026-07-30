import re
from urllib.parse import urlparse
from typing import List, Dict, Any
from ._shared import (
    get_domain_from_url, 
    is_raw_ip, 
    load_whitelist_db, 
    extract_all_urls,
    check_typosquatting,
    is_redirect_or_shortened,
    expand_redirect_url,
    is_private_or_restricted_target
)

def scan_text_and_urls(text_input: str) -> Dict[str, Any]:
    """
    Smart Rule Engine 2.0 & Agentic Pre-fetch Injection (v0.2.2 - Zero-Trust Armor).
    Tuân thủ giao tiếp Cố Vấn Đồng Cảm (Empathetic UX) - Người dùng là chốt chặn cuối.
    """
    db = load_whitelist_db()
    company_domains = list(db.get("company_domains", []))
    trusted_domains = set(db.get("trusted_external_domains", []))
    high_risk_exts = tuple(db.get("high_risk_extensions", []))
    suspicious_keywords = db.get("suspicious_keywords_in_url", [])

    urls = extract_all_urls(text_input)
    
    # Trường hợp 0: Không có URL nào trong nội dung
    if not urls:
        return {
            "extracted_urls": [],
            "needs_llm_call": False,
            "deterministic_result": {
                "risk_level": "SAFE",
                "risk_score": 2, 
                "confidence_score": 0.95,
                "confidence_level": "HIGH",
                "suspicious_elements": [],
                "recommendation": "✅ Trợ lý PhishShield đã kiểm duyệt: Trong văn bản không chứa liên kết web nào. Về mặt phân tích đường link là hoàn toàn an toàn.",
                "analysis_source": "SMART_RULE_ENGINE_2.0 (No LLM Called)"
            },
            "url_analyses": []
        }

    url_analyses = []
    has_unknown_or_suspicious = False
    has_definite_danger = False
    danger_reasons = []

    for url in urls:
        domain = get_domain_from_url(url)
        if not domain:
            continue
            
        analysis = {
            "url": url, 
            "domain": domain, 
            "status": "UNKNOWN", 
            "reasons": [],
            "redirect_audit": None,
            "typosquatting_audit": None
        }
        
        # Bước A0: Kiểm định Zero-Trust Armor (Chặn Giao thức cấm & Tấn công nội bộ SSRF)
        cleaned_url = url if re.match(r'^[a-zA-Z]+://', url) else "http://" + url
        try:
            scheme = (urlparse(cleaned_url).scheme or "").lower()
        except Exception:
            scheme = "http"
            
        if scheme not in ["http", "https"]:
            analysis["status"] = "DANGER_BY_RULE"
            reason = f"🚨 BẢO VỆ ZERO-TRUST: Liên kết '{url}' lạm dụng giao thức cấm '{scheme}://' thay vì HTTP/HTTPS chuẩn web. Nguy cơ xâm phạm tài liệu hệ thống!"
            analysis["reasons"].append(reason)
            has_definite_danger = True
            danger_reasons.append(reason)
            url_analyses.append(analysis)
            continue
            
        if is_private_or_restricted_target(domain):
            analysis["status"] = "DANGER_BY_RULE"
            reason = f"🛡️ BẢO VỆ ZERO-TRUST: Liên kết '{url}' trỏ ngầm về vùng IP/Hành lang mạng nội bộ (SSRF / Localhost / Cloud Metadata). Đây là hành vi thâm nhập trái phép!"
            analysis["reasons"].append(reason)
            has_definite_danger = True
            danger_reasons.append(reason)
            url_analyses.append(analysis)
            continue

        # Bước A: Kiểm tra xem link có bị rút gọn hoặc lồng Redirect hay không
        is_redirect = is_redirect_or_shortened(url, domain)
        if is_redirect:
            audit_res = expand_redirect_url(url, timeout=3.0)
            analysis["redirect_audit"] = audit_res
            
            if audit_res.get("is_zero_trust_violation"):
                analysis["status"] = "DANGER_BY_RULE"
                reason = audit_res.get("error_message", "Liên kết bị khiên bảo mật Zero-Trust từ chối thực thi.")
                analysis["reasons"].append(reason)
                has_definite_danger = True
                danger_reasons.append(reason)
                url_analyses.append(analysis)
                continue
            elif audit_res.get("is_dangerous_executable_file"):
                analysis["status"] = "DANGER_BY_RULE"
                reason = f"Đường link nhúng '{url}' bị thấu thị trỏ thẳng về một tệp tin nén/thực thi nhạy cảm: {audit_res['unmasked_destination']}."
                analysis["reasons"].append(reason)
                has_definite_danger = True
                danger_reasons.append(reason)
                url_analyses.append(analysis)
                continue
            else:
                analysis["status"] = "NEEDS_LLM"
                analysis["reasons"].append(f"Liên kết rút gọn / chuyển hướng mang địa chỉ gốc là '{url}' được Tool cách ly giải mã trỏ sang đích đến: '{audit_res['unmasked_destination']}'.")
                has_unknown_or_suspicious = True
                url_analyses.append(analysis)
                continue

        # Bước B: Kiểm tra Whitelist công ty & Trusted domains
        is_trusted = False
        for td in (set(company_domains) | trusted_domains):
            if domain == td or domain.endswith("." + td):
                is_trusted = True
                break
                
        if is_trusted:
            analysis["status"] = "SAFE_BY_RULE"
            analysis["reasons"].append(f"Tên miền '{domain}' thuộc hệ thống hạ tầng quen thuộc và uy tín của công ty/đối tác.")
            url_analyses.append(analysis)
            continue
            
        # Bước C: Kiểm tra Địa chỉ IP tĩnh (Dấu hiệu Phishing điển hình)
        if is_raw_ip(domain):
            analysis["status"] = "DANGER_BY_RULE"
            reason = f"Đường link '{url}' giao tiếp trực tiếp qua dãy địa chỉ IP thô '{domain}' thay vì tên miền định dạng hợp pháp."
            analysis["reasons"].append(reason)
            has_definite_danger = True
            danger_reasons.append(reason)
            url_analyses.append(analysis)
            continue

        # Bước D: Kiểm tra nhái nhãn hiệu Levenshtein & Typosquatting (Thuật toán 2.0)
        typo_res = check_typosquatting(domain, company_domains)
        analysis["typosquatting_audit"] = typo_res
        if typo_res.get("is_typosquatting"):
            analysis["status"] = "DANGER_BY_RULE"
            reason = typo_res["reason"]
            analysis["reasons"].append(reason)
            has_definite_danger = True
            danger_reasons.append(reason)
            url_analyses.append(analysis)
            continue

        # Bước E: Kiểm tra Heuristic rủi ro cao (Đuôi domain độc hại + Từ khóa đáng ngờ)
        is_high_risk_ext = any(domain.endswith(ext) for ext in high_risk_exts)
        has_suspicious_kw = any(kw in url.lower() for kw in suspicious_keywords)
        
        if is_high_risk_ext and has_suspicious_kw:
            analysis["status"] = "DANGER_BY_RULE"
            reason = f"Tên miền ngoài '{domain}' sử dụng đuôi mở rộng độ rủi ro cao đi kèm các từ khóa thao túng bảo mật nhạy cảm."
            analysis["reasons"].append(reason)
            has_definite_danger = True
            danger_reasons.append(reason)
        else:
            analysis["status"] = "NEEDS_LLM"
            if has_suspicious_kw:
                analysis["reasons"].append(f"Liên kết ngoài mang từ khóa thúc ép hành động: {[kw for kw in suspicious_keywords if kw in url.lower()]}.")
            if not analysis["reasons"]:
                analysis["reasons"].append(f"Tên miền bên ngoài '{domain}' chưa từng xuất hiện trong cơ sở tri thức đã xác minh của công ty.")
            has_unknown_or_suspicious = True
            
        url_analyses.append(analysis)

    # Quyết định điều phối với Ngôn ngữ Đồng Cảm & Khiên Zero-Trust (Empathetic Copilot Communication)
    if has_definite_danger:
        return {
            "extracted_urls": urls,
            "needs_llm_call": False,
            "deterministic_result": {
                "risk_level": "DANGER",
                "risk_score": 96, 
                "confidence_score": 0.99, 
                "confidence_level": "HIGH",
                "suspicious_elements": danger_reasons,
                "recommendation": "🛡️ Góc Cố Vấn từ Trợ lý AI: Hệ thống rà soát phát hiện dấu hiệu giả mạo thương hiệu hoặc vi phạm chính sách tường lửa nội bộ trên đường link trong email. Đây là thủ thuật đánh tráo kỹ thuật thường dùng trong kịch bản Tấn công mạng/Phishing. Trợ lý đề xuất bạn cân nhắc không thao tác tại liên kết này và chuyển hồ sơ này sang cho phòng IT Kỹ thuật thẩm định nhé!",
                "analysis_source": "SMART_RULE_ENGINE_2.0 (No LLM Called - Saved Token)"
            },
            "url_analyses": url_analyses
        }
        
    if all(u["status"] == "SAFE_BY_RULE" for u in url_analyses):
        return {
            "extracted_urls": urls,
            "needs_llm_call": False,
            "deterministic_result": {
                "risk_level": "SAFE",
                "risk_score": 2, 
                "confidence_score": 0.95,
                "confidence_level": "HIGH",
                "suspicious_elements": [],
                "recommendation": "✅ Trợ lý PhishShield đã kiểm tra: Toàn bộ đường link trong nội dung đều hướng về trang thông tin hợp pháp và quen thuộc. Bạn hoàn toàn an tâm tiếp tục công việc nhé!",
                "analysis_source": "SMART_RULE_ENGINE_2.0 (No LLM Called - Saved Token)"
            },
            "url_analyses": url_analyses
        }

    # Các ca link lạ, rút gọn Bitly, chuyển hướng hoặc mờ hồ -> CHUYỂN LLM AGENT REASONING!
    return {
        "extracted_urls": urls,
        "needs_llm_call": True,
        "deterministic_result": None,
        "url_analyses": url_analyses
    }
