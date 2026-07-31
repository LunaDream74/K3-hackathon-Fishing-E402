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
    is_private_or_restricted_target,
    KNOWN_SHORTENERS,
    load_active_memory
)

def analyze_social_engineering_lures(text: str) -> Dict[str, Any]:
    """
    Bộ quét thủ thuật thao túng tâm lý (Social Engineering Text Heuristics) tại Tầng 1.
    Đóng vai trò là Bộ số nhân rủi ro (Risk Multiplier) để ra quyết định theo hướng Xác Suất Đồng Quy.
    """
    lower_text = text.lower()
    
    urgency_kws = ["khẩn", "ngay lập tức", "trong vòng 24", "trong 30 phút", "hạn chót", "trước 17:00", "urgent", "immediately", "khắc phục gấp", "gấp", "deadline", "expires"]
    threat_kws = ["bị khoá", "bị khóa", "đình chỉ", "hủy tài khoản", "tạm tháo", "rò rỉ", "vi phạm", "tạm dừng", "hủy bỏ", "khoá tài khoản", "reset your password", "thay đổi thông tin"]
    reward_kws = ["thưởng tết", "quà tặng", "chi trả", "tăng lương", "lì xì", "trúng thưởng", "voucher", "thù lao", "miễn phí"]
    
    found_urgency = [w for w in urgency_kws if w in lower_text]
    found_threat = [w for w in threat_kws if w in lower_text]
    found_reward = [w for w in reward_kws if w in lower_text]
    
    all_matched = list(dict.fromkeys(found_urgency + found_threat + found_reward))
    categories = []
    if found_urgency:
        categories.append("thúc ép thời gian khẩn cấp")
    if found_threat:
        categories.append("đe dọa hình phạt/khóa tài khoản")
    if found_reward:
        categories.append("lôi kéo bằng phần thưởng/tài chính")
        
    if all_matched:
        cat_str = " và ".join(categories)
        kw_str = ", ".join(f"'{k}'" for k in all_matched[:4])
        summary = f"⚠️ Thủ thuật thao túng tâm lý (Social Engineering): Văn bản sử dụng chiến thuật {cat_str} ({kw_str}) nhằm gây xáo xộn cảm xúc và thúc ép người dùng bấm liên kết mà không kịp suy xét kỹ lưỡng."
    else:
        summary = ""
        
    return {
        "has_lures": len(all_matched) > 0,
        "matched_categories": categories,
        "matched_keywords": all_matched,
        "summary_reason": summary
    }

def scan_text_and_urls(text_input: str) -> Dict[str, Any]:
    """
    Smart Rule Engine 2.0 & Actionable Copilot Toolkit (v0.4.0 - Universal Auto-Drafting & Probabilistic Fusion).
    Tuân thủ giao tiếp Cố Vấn Đồng Cảm, phân tích song hành URL + Văn Bản, cung cấp 100% bản nháp hành động lập thì.
    """
    db = load_whitelist_db()
    mem_db = load_active_memory()
    company_domains = list(db.get("company_domains", []))
    trusted_domains = set(db.get("trusted_external_domains", []))
    human_whitelist = set(mem_db.get("human_whitelisted_domains", []))
    human_blacklist = set(mem_db.get("human_blacklisted_domains", []))
    high_risk_exts = tuple(db.get("high_risk_extensions", []))
    suspicious_keywords = db.get("suspicious_keywords_in_url", [])

    urls = extract_all_urls(text_input)
    soc_eng = analyze_social_engineering_lures(text_input)
    
    # Trường hợp 0: Không có URL nào trong nội dung
    if not urls:
        risk_sc = 15 if soc_eng["has_lures"] else 2
        rec = (f"✅ Trợ lý PhishShield đã rà soát: Dù văn bản có tiếng nói gấp gáp hoặc chú ý ({', '.join(soc_eng['matched_keywords'][:3])}), nhưng nội dung hoàn toàn không chứa đường dẫn liên kết hay trang web lạ nào. Bạn có thể yên tâm đọc thông báo." 
               if soc_eng["has_lures"] else 
               "✅ Trợ lý PhishShield đã kiểm duyệt: Trong văn bản không chứa liên kết web nào. Về mặt phân tích đường link là hoàn toàn an toàn.")
        return {
            "extracted_urls": [],
            "social_engineering_audit": soc_eng,
            "needs_llm_call": False,
            "deterministic_result": {
                "risk_level": "SAFE",
                "risk_score": risk_sc, 
                "confidence_score": 0.95,
                "confidence_level": "HIGH",
                "suspicious_elements": [],
                "recommendation": rec,
                "action_draft": {
                    "draft_type": "REPLY_ACK",
                    "target_recipient": "Người gửi Email / Đối tác",
                    "message_title": "💡 Gợi ý thao tác: Phản hồi xác nhận đã đọc thông báo",
                    "message_template": "Cảm ơn bạn/anh chị. Mình đã đọc và tiếp nhận trọn vẹn nội dung email thông báo này nhé!"
                },
                "analysis_source": "SMART_RULE_ENGINE_2.0 (Probabilistic Fusion & Zero Token)"
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
        
        # Bước A-1: Kiểm tra Trí Nhớ Động từ phản hồi con người (Active Memory Blacklist - Human RLHF)
        if domain in human_blacklist or any(domain.endswith("." + bd) for bd in human_blacklist if bd):
            analysis["status"] = "DANGER_BY_RULE"
            reason = f"🧠 TRÍ NHỚ ĐỘNG (Active Memory - Human RLHF): Tên miền '{domain}' đã từng bị người dùng trong tổ chức gán nhãn Độc hại. Hệ thống từ chối truy xuất ngay lập tức!"
            analysis["reasons"].append(reason)
            has_definite_danger = True
            danger_reasons.append(reason)
            url_analyses.append(analysis)
            continue
        
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
            elif (domain in KNOWN_SHORTENERS or any(domain.endswith(s) for s in KNOWN_SHORTENERS)) and soc_eng["has_lures"]:
                analysis["status"] = "DANGER_BY_RULE"
                reason = f"🚨 CẢNH BÁO CAO ĐỘ: Liên kết rút gọn ẩn danh '{url}' đi kèm thủ thuật thúc ép/đe dọa ('{', '.join(soc_eng['matched_keywords'][:2])}'). Đây là kịch bản lừa đảo điển hình!"
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

        # Bước B: Kiểm tra Whitelist công ty, Trusted domains & Trí Nhớ Động (Human RLHF Whitelist)
        is_trusted = False
        is_human_rlhf_safe = False
        for td in (set(company_domains) | trusted_domains | human_whitelist):
            if domain == td or domain.endswith("." + td):
                is_trusted = True
                if td in human_whitelist and td not in company_domains and td not in trusted_domains:
                    is_human_rlhf_safe = True
                break
                
        if is_trusted:
            analysis["status"] = "SAFE_BY_RULE"
            if is_human_rlhf_safe:
                analysis["reasons"].append(f"🧠 TRÍ NHỚ ĐỘNG (Active Memory - Human RLHF): Tên miền '{domain}' đã được chuyên viên/người dùng xác nhận An toàn trong lịch sử phản hồi.")
            else:
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

    # Quyết định điều phối Xác Suất Đồng Quy với Ngôn ngữ Đồng Cảm & Khử Lặp Tuyệt Đối
    if has_definite_danger:
        # Khử lặp lý do 100% bằng dict.fromkeys
        unique_danger_reasons = list(dict.fromkeys(danger_reasons))
        if soc_eng["has_lures"]:
            unique_danger_reasons.append(soc_eng["summary_reason"])
            risk_score = 98  # Cộng hưởng cả 2 trục Văn bản & URL
        else:
            risk_score = 92  # Chỉ thuần túy lỗi từ tên miền độc hại
            
        # Lấy tối đa 2 lý do sắc bén nhất cho vào câu nháp báo cáo để tránh dài dòng
        summary_reasons_for_draft = "; ".join(unique_danger_reasons[:2])
            
        return {
            "extracted_urls": urls,
            "social_engineering_audit": soc_eng,
            "needs_llm_call": False,
            "deterministic_result": {
                "risk_level": "DANGER",
                "risk_score": risk_score, 
                "confidence_score": 0.99, 
                "confidence_level": "HIGH",
                "suspicious_elements": unique_danger_reasons,
                "recommendation": "🛡️ Góc Cố Vấn từ Trợ lý AI: Hệ thống phát hiện sự cộng hưởng giữa liên kết giả mạo thương hiệu/tính năng mờ ám và thủ thuật thúc ép người dùng trong email. Trợ lý đề xuất bạn không nhấp mở trang đích và bấm Copy bản nháp dưới đây để gửi báo cáo nhanh cho phòng IT Kỹ thuật xử lý nhé!",
                "action_draft": {
                    "draft_type": "INCIDENT_REPORT",
                    "target_recipient": "Phòng Bảo Mật IT / SOC Helpdesk",
                    "message_title": "🚨 Gợi ý thao tác: Copy Báo cáo khẩn vi phạm an ninh gửi Đội IT",
                    "message_template": f"Kính gửi Phòng Bảo Mật IT, hệ thống PhishShield trên máy tôi vừa tự động phát hiện một email có tính chất rủi ro cao mang bằng chứng kỹ thuật: '{summary_reasons_for_draft}'. Nhờ anh em kỹ thuật kiểm nghiệm và chặn tên miền/IP này trên toàn mạng công ty nhé!"
                },
                "analysis_source": "SMART_RULE_ENGINE_2.0 (Probabilistic Fusion & Zero Token)"
            },
            "url_analyses": url_analyses
        }
        
    if all(u["status"] == "SAFE_BY_RULE" for u in url_analyses):
        # Dù văn bản có giục giã khẩn cấp hay nhắc nhở hạn chót, vì toàn bộ Link thuộc Whitelist hợp pháp -> AN TOÀN!
        risk_score = 10 if soc_eng["has_lures"] else 3
        rec = (f"✅ Trợ lý PhishShield đã kiểm chứng: Toàn bộ liên kết trong thư đều trỏ về cổng thông tin hợp pháp và xác thực của công ty/đối tác. Dù thông báo có tính chất gấp gáp hoặc liên quan đến hạn chót ('{', '.join(soc_eng['matched_keywords'][:3])}'), bạn hoàn toàn có thể yên tâm tiếp tục công việc trên hệ thống an toàn nhé!" 
               if soc_eng["has_lures"] else 
               "✅ Trợ lý PhishShield đã kiểm tra: Toàn bộ đường link trong nội dung đều hướng về trang thông tin hợp pháp và quen thuộc. Bạn hoàn toàn an tâm tiếp tục công việc nhé!")
        
        return {
            "extracted_urls": urls,
            "social_engineering_audit": soc_eng,
            "needs_llm_call": False,
            "deterministic_result": {
                "risk_level": "SAFE",
                "risk_score": risk_score, 
                "confidence_score": 0.95,
                "confidence_level": "HIGH",
                "suspicious_elements": [],
                "recommendation": rec,
                "action_draft": {
                    "draft_type": "REPLY_ACK",
                    "target_recipient": "Người gửi Email / Đồng nghiệp",
                    "message_title": "💡 Gợi ý thao tác: Copy tin nhắn xác nhận tiếp nhận tài liệu an toàn",
                    "message_template": "Cảm ơn bạn/anh chị đã gửi thông tin. Mình đã tiếp nhận tài liệu và truy cập được liên kết hướng dẫn trên cổng hệ thống an toàn của công ty thành công nhé!"
                },
                "analysis_source": "SMART_RULE_ENGINE_2.0 (Probabilistic Fusion & Zero Token)"
            },
            "url_analyses": url_analyses
        }

    # Các ca link lạ, rút gọn Bitly, chuyển hướng hoặc mờ hồ -> CHUYỂN LLM AGENT REASONING KÈM BỘ GIẢI VĂN BẢN!
    return {
        "extracted_urls": urls,
        "social_engineering_audit": soc_eng,
        "needs_llm_call": True,
        "deterministic_result": None,
        "url_analyses": url_analyses
    }
