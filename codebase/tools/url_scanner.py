from typing import List, Dict, Any
from ._shared import get_domain_from_url, is_raw_ip, load_whitelist_db, extract_all_urls

def scan_text_and_urls(text_input: str) -> Dict[str, Any]:
    """
    Hàm chủ lực của Tool xử lý URL.
    Triển khai nguyên tắc: "Cái gì làm đơn giản bằng Rule-based được thì làm ngay mà KHÔNG GỌI LLM".
    
    Trả về cấu trúc:
    {
        "extracted_urls": List[str],
        "needs_llm_call": bool,       # Nếu False -> Trả ngay kết quả cho người dùng, tiết kiệm 100% chi phí và thời gian
        "deterministic_result": Dict, # Có giá trị nếu needs_llm_call == False
        "url_analyses": List[Dict]    # Thông tin sơ bộ cho từng URL để đưa vào prompt cho LLM nếu cần
    }
    """
    db = load_whitelist_db()
    company_domains = set(db.get("company_domains", []))
    trusted_domains = set(db.get("trusted_external_domains", []))
    high_risk_exts = tuple(db.get("high_risk_extensions", []))
    suspicious_keywords = db.get("suspicious_keywords_in_url", [])

    urls = extract_all_urls(text_input)
    
    # Trường hợp 1: Không có URL nào trong nội dung
    if not urls:
        return {
            "extracted_urls": [],
            "needs_llm_call": False,
            "deterministic_result": {
                "risk_level": "SAFE",
                "risk_score": 0,
                "suspicious_elements": [],
                "recommendation": "Trong email/nội dung không chứa bất kỳ đường link (URL) nào. Yếu tố liên kết an toàn.",
                "analysis_source": "RULE_ENGINE (No LLM Called)"
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
            
        analysis = {"url": url, "domain": domain, "status": "UNKNOWN", "reasons": []}
        
        # 1. Kiểm tra Whitelist công ty & Trusted domains (Quy tắc an toàn tuyệt đối)
        is_trusted = False
        for td in (company_domains | trusted_domains):
            if domain == td or domain.endswith("." + td):
                is_trusted = True
                break
                
        if is_trusted:
            analysis["status"] = "SAFE_BY_RULE"
            analysis["reasons"].append(f"Tên miền '{domain}' nằm trong danh sách Whitelist chính thức được tin tưởng.")
            url_analyses.append(analysis)
            continue
            
        # 2. Kiểm tra Địa chỉ IP tĩnh (Dính IP tĩnh không thuộc Whitelist -> 100% Độc hại)
        if is_raw_ip(domain):
            analysis["status"] = "DANGER_BY_RULE"
            reason = f"Đường link '{url}' sử dụng địa chỉ IP trực tiếp '{domain}' thay vì tên miền (Dấu hiệu điển hình của máy chủ Phishing)."
            analysis["reasons"].append(reason)
            url_analyses.append(analysis)
            has_definite_danger = True
            danger_reasons.append(reason)
            continue

        # 3. Kiểm tra Heuristic rủi ro cao (Đuôi domain độc hại + Từ khóa đáng ngờ / Giả danh công ty - Typosquatting)
        is_high_risk_ext = any(domain.endswith(ext) for ext in high_risk_exts)
        has_suspicious_kw = any(kw in url.lower() for kw in suspicious_keywords)
        
        # Kiểm tra giả danh thương hiệu (Brand spoofing / typosquatting sơ bộ)
        # VD: vinai-support.tk hoặc vlearn-secure.xyz (chứa chữ vinai/vlearn nhưng không thuộc domain chính thức)
        brand_spoof = any(brand.split('.')[0] in domain for brand in company_domains)

        if is_high_risk_ext and (has_suspicious_kw or brand_spoof):
            # Cả đuôi rủi ro và từ khóa giả mạo -> Khẳng định độc hại mà không cần hỏi LLM
            analysis["status"] = "DANGER_BY_RULE"
            reason = f"Tên miền '{domain}' sử dụng phần mở rộng độ rủi ro cao và có từ khóa giả danh/thao túng bảo mật."
            analysis["reasons"].append(reason)
            has_definite_danger = True
            danger_reasons.append(reason)
        else:
            # Các trường hợp tên miền lạ khác chưa từng biết tới -> Chuyển cho LLM đánh giá ngữ cảnh
            analysis["status"] = "NEEDS_LLM"
            if brand_spoof:
                analysis["reasons"].append(f"Nghi vấn giả danh thương hiệu nội bộ (Typosquatting) từ tên miền lạ '{domain}'.")
            if has_suspicious_kw:
                analysis["reasons"].append(f"Liên kết có chứa từ khóa thúc ép/xác thực nhạy cảm: {[kw for kw in suspicious_keywords if kw in url.lower()]}.")
            if not analysis["reasons"]:
                analysis["reasons"].append(f"Tên miền bên ngoài '{domain}' chưa nằm trong danh sách kiểm chứng của công ty.")
            has_unknown_or_suspicious = True
            
        url_analyses.append(analysis)

    # Quyết định điều phối: Có cần gọi LLM hay không?
    # Nếu có ít nhất 1 URL độc hại rõ ràng bởi luật (DANGER_BY_RULE), và không cần giải nghĩa phức tạp -> Trả ngay Danger!
    if has_definite_danger and not has_unknown_or_suspicious:
        return {
            "extracted_urls": urls,
            "needs_llm_call": False,
            "deterministic_result": {
                "risk_level": "DANGER",
                "risk_score": 95,
                "suspicious_elements": danger_reasons,
                "recommendation": "CẢNH BÁO: Phát hiện liên kết mang dấu hiệu lừa đảo rõ rệt. Tuyệt đối KHÔNG BẤM VÀO ĐƯỜNG LINK TRÊN. Hãy thông báo ngay cho bộ phận Kỹ thuật/IT.",
                "analysis_source": "RULE_ENGINE (No LLM Called - Saved Token)"
            },
            "url_analyses": url_analyses
        }
        
    # Nếu tất cả các URL đều an toàn 100% trong Whitelist
    if all(u["status"] == "SAFE_BY_RULE" for u in url_analyses):
        return {
            "extracted_urls": urls,
            "needs_llm_call": False,
            "deterministic_result": {
                "risk_level": "SAFE",
                "risk_score": 0,
                "suspicious_elements": [],
                "recommendation": "Tất cả đường link trong nội dung đều thuộc tên miền chính thức và an toàn của công ty hoặc đối tác tin cậy.",
                "analysis_source": "RULE_ENGINE (No LLM Called - Saved Token)"
            },
            "url_analyses": url_analyses
        }

    # Nếu có URL lạ hoặc nghi vấn phức tạp cần tư duy ngữ cảnh -> CẦN GỌI LLM API!
    return {
        "extracted_urls": urls,
        "needs_llm_call": True,
        "deterministic_result": None,
        "url_analyses": url_analyses
    }
