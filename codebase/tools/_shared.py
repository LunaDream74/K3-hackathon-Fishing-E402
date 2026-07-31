import json
import re
import urllib.request
import urllib.parse
from urllib.parse import urlparse
from pathlib import Path
from typing import Dict, Any, List, Optional
import ipaddress

def get_domain_from_url(url: str) -> str:
    """
    Trích xuất tên miền chính (hostname) từ chuỗi URL.
    Nếu URL thiếu scheme (http/https), tự động thêm http:// để parse.
    """
    cleaned_url = url.strip()
    if not re.match(r'^[a-zA-Z]+://', cleaned_url):
        cleaned_url = "http://" + cleaned_url
    
    try:
        parsed = urlparse(cleaned_url)
        hostname = parsed.hostname or ""
        if hostname.startswith("www."):
            hostname = hostname[4:]
        return hostname.lower()
    except Exception:
        return ""

def is_raw_ip(hostname: str) -> bool:
    """
    Kiểm tra xem hostname có phải là địa chỉ IP tĩnh không.
    """
    ipv4_pattern = re.compile(
        r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
        r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    )
    return bool(ipv4_pattern.match(hostname))

def load_whitelist_db() -> Dict[str, Any]:
    """
    Tải cơ sở dữ liệu Whitelist và từ khóa rủi ro từ thư mục company_policy.
    """
    current_dir = Path(__file__).resolve().parent
    policy_path = current_dir.parent / "company_policy" / "domain-whitelist.json"
    
    try:
        with open(policy_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Warning] Không thể tải domain-whitelist.json: {e}. Sử dụng danh sách rỗng.")
        return {
            "company_domains": [],
            "trusted_external_domains": [],
            "high_risk_extensions": [],
            "suspicious_keywords_in_url": []
        }

def load_active_memory() -> Dict[str, Any]:
    """
    Tải cơ sở dữ liệu Trí Nhớ Động (Active Memory) lưu trữ kết quả học tập từ Human RLHF Feedback.
    """
    current_dir = Path(__file__).resolve().parent
    memory_path = current_dir.parent / "company_policy" / "active_memory.json"
    
    try:
        with open(memory_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {
            "human_whitelisted_domains": [],
            "human_blacklisted_domains": [],
            "rlhf_feedback_history": []
        }

def update_active_memory(domain: str, verdict: str, note: str = "") -> bool:
    """
    Nạp tri thức từ quyết định phán xét của con người (Human RLHF) vào Trí Nhớ Động.
    - Nếu verdict == 'SAFE': Đưa vào human_whitelisted_domains (loại khỏi blacklist nếu có).
    - Nếu verdict == 'DANGER': Đưa vào human_blacklisted_domains (loại khỏi whitelist nếu có).
    """
    if not domain:
        return False
    current_dir = Path(__file__).resolve().parent
    memory_path = current_dir.parent / "company_policy" / "active_memory.json"
    data = load_active_memory()
    
    domain_clean = domain.lower().strip()
    import datetime
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    if verdict.upper() == "SAFE":
        if domain_clean in data.get("human_blacklisted_domains", []):
            data["human_blacklisted_domains"].remove(domain_clean)
        if domain_clean not in data.get("human_whitelisted_domains", []):
            data.setdefault("human_whitelisted_domains", []).append(domain_clean)
    elif verdict.upper() in ["DANGER", "PHISHING", "DOUBT"]:
        if domain_clean in data.get("human_whitelisted_domains", []):
            data["human_whitelisted_domains"].remove(domain_clean)
        if domain_clean not in data.get("human_blacklisted_domains", []):
            data.setdefault("human_blacklisted_domains", []).append(domain_clean)
            
    history_entry = {
        "timestamp": timestamp,
        "domain": domain_clean,
        "override_verdict": verdict.upper(),
        "source": "Human_RLHF_Feedback",
        "note": note or f"Người dùng đổi nhãn phán xét thành {verdict.upper()} (Active Memory Evolving)."
    }
    data.setdefault("rlhf_feedback_history", []).append(history_entry)
    
    try:
        with open(memory_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"[Error] Không thể ghi Trí Nhớ Động: {e}")
        return False

def extract_all_urls(text: str) -> List[str]:
    """
    Sử dụng biểu thức chính quy (Regex) để trích xuất toàn bộ đường link trong văn bản email.
    Bao gồm cả các giao thức phi chuần như file://, ftp:// để đưa vào trạm kiểm soát Zero-Trust.
    """
    url_pattern = re.compile(
        r'(?:(?:https?|ftp|file|gopher|data)://[-a-zA-Z0-9()@:%_\+.~#?&//=]+|'
        r'(?:[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b|'
        r'(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)|'
        r'localhost)'
        r'(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*))',
        re.IGNORECASE
    )
    
    matches = url_pattern.findall(text)
    valid_urls = []
    for m in matches:
        m_clean = m.rstrip(".,;!?:')\"")
        if "." in m_clean or re.match(r'^[a-zA-Z]+://', m_clean) or "localhost" in m_clean:
            valid_urls.append(m_clean)
            
    return list(dict.fromkeys(valid_urls))

# =============================================================================
# THUẬT TOÁN LEVENSHTEIN & KIỂM TRA TYPOSQUATTING (SMART RULE ENGINE 2.0)
# =============================================================================
def levenshtein_distance(s1: str, s2: str) -> int:
    """
    Tính khoảng cách chỉnh sửa chuỗi (Levenshtein distance) bằng Python thuần.
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (0 if c1 == c2 else 1)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]

def check_typosquatting(domain: str, company_domains: List[str]) -> Dict[str, Any]:
    """
    Phát hiện các đòn giả danh thương hiệu tinh vi (Typosquatting & Brand Spoofing).
    """
    res = {"is_typosquatting": False, "target_brand": "", "distance": -1, "reason": ""}
    
    for cd in company_domains:
        if domain == cd or domain.endswith("." + cd):
            return res

    domain_part = domain.split('.')[0] 
    
    for cd in company_domains:
        cd_part = cd.split('.')[0] 
        
        dist_full = levenshtein_distance(domain, cd)
        dist_part = levenshtein_distance(domain_part, cd_part)
        
        # Guard an toàn: chỉ check chuỗi con với nhãn hiệu có độ dài >= 4
        if dist_full <= 2 or (dist_part <= 2 and len(cd_part) >= 4):
            res["is_typosquatting"] = True
            res["target_brand"] = cd
            res["distance"] = min(dist_full, dist_part)
            res["reason"] = f"Tên miền '{domain}' được cố tình viết nhái thương hiệu nội bộ '{cd}' (Khoảng cách Levenshtein: {res['distance']} ký tự)."
            return res

        if cd_part in domain and not domain.endswith("." + cd):
            res["is_typosquatting"] = True
            res["target_brand"] = cd
            res["reason"] = f"Tên miền ngoài '{domain}' mạo nhận chứa trực tiếp tên thương hiệu '{cd_part}' của công ty nhằm gây nhầm lẫn (Brand Spoofing)."
            return res

    return res

# =============================================================================
# ZERO-TRUST SECURITY ARMOR (CHỐNG SSRF, SCHEME ABUSE & BẢO DIỆN TOOL)
# =============================================================================
KNOWN_SHORTENERS = {
    "bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", 
    "is.gd", "buff.ly", "cutt.ly", "rebrand.ly", "fb.me", "q.vu"
}

REDIRECT_KEYWORDS = [
    "?url=", "&url=", "?q=", "&q=", "redirect_to=", 
    "redirect_url=", "out=", "goto=", "link=", "return_to="
]

def is_private_or_restricted_target(hostname: str) -> bool:
    """
    Khiên chống SSRF & Chặn tải trang nội bộ/Đám mây (Zero-Trust Guard).
    Phát hiện mọi dải IP tĩnh riêng (127.0.0.1, 10.x, 192.168.x, 169.254.x) và host nội bộ.
    """
    if not hostname:
        return True
    
    hostname_lower = hostname.lower()
    restricted_hosts = {"localhost", "metadata.google.internal", "kubernetes.default"}
    if hostname_lower in restricted_hosts or hostname_lower.endswith(".local") or hostname_lower.endswith(".internal"):
        return True
        
    try:
        # Sử dụng module chuẩn ipaddress của Python để bắt gọn toàn bộ dải IP nội bộ/nhạy cảm
        ip_obj = ipaddress.ip_address(hostname)
        if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_reserved or ip_obj.is_unspecified:
            return True
        # Đặc biệt kiểm tra cụ thể IP metadata của AWS/Cloud
        if str(ip_obj) == "169.254.169.254":
            return True
    except ValueError:
        # Không phải số IP thô thì bỏ qua bước kiểm tra IP
        pass
        
    return False

def is_redirect_or_shortened(url: str, domain: str) -> bool:
    """
    Nhận diện link rút gọn hoặc link mang tham số chuyển hướng trá hình.
    """
    if domain in KNOWN_SHORTENERS or any(domain.endswith(s) for s in KNOWN_SHORTENERS):
        return True
    
    url_lower = url.lower()
    for kw in REDIRECT_KEYWORDS:
        if kw in url_lower:
            return True
    return False

def expand_redirect_url(url: str, timeout: float = 3.0) -> Dict[str, Any]:
    """
    Tool Cách ly (Sandboxed Tool v0.2.2 - Military-Grade Zero-Trust Armor).
    - Bức Tường 1 (Scheme Firewall): Chỉ chấp nhận HTTP/HTTPS, chặn đứng file://, ftp://, gopher://...
    - Bức Tường 2 (SSRF Armor): Từ chối kết nối tới các hostname/IP nội bộ (127.0.0.1, localhost, 169.254.x...).
    - Bức Tường 3 (HEAD Only): Tắt JavaScript, từ chối tải nội dung body để cấm Zip Bomb & Malware executable.
    """
    cleaned_url = url.strip()
    if not re.match(r'^[a-zA-Z]+://', cleaned_url):
        cleaned_url = "http://" + cleaned_url
        
    try:
        parsed = urlparse(cleaned_url)
        scheme = (parsed.scheme or "").lower()
        hostname = (parsed.hostname or "").lower()
        
        # Bức Tường 1: Kiểm soát Giao thức (Scheme Firewall)
        if scheme not in ["http", "https"]:
            return {
                "original_url": url,
                "unmasked_destination": url,
                "is_redirected": False,
                "is_dangerous_executable_file": False,
                "is_zero_trust_violation": True,
                "status": "BLOCKED_BY_SCHEME_FIREWALL",
                "error_message": f"🚨 BẢO VỆ ZERO-TRUST: Phát hiện đòn lạm dụng giao thức cấm '{scheme}://'. Hệ thống từ chối truy xuất để bảo vệ thiết bị!"
            }
            
        # Bức Tường 2: Khiên Chống SSRF & Đột Nhập Nội Bộ (SSRF Armor)
        if is_private_or_restricted_target(hostname):
            return {
                "original_url": url,
                "unmasked_destination": url,
                "is_redirected": False,
                "is_dangerous_executable_file": False,
                "is_zero_trust_violation": True,
                "status": "BLOCKED_BY_SSRF_ARMOR",
                "error_message": f"🛡️ BẢO VỆ ZERO-TRUST: Phát hiện liên kết mục tiêu trỏ về vùng IP/hạ tầng nội bộ ('{hostname}'). Hệ thống từ chối kết nối để ngăn chặn tấn công SSRF!"
            }
            
        # Bức Tường 3: Thực thi gọi HEAD nhã nhặn, cấm thực thi scripts & cấm tải file
        req = urllib.request.Request(
            cleaned_url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) PhishShield-ZeroTrust-Audit/2.0'},
            method='HEAD'
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            final_url = response.geturl()
            content_type = response.headers.get("Content-Type", "").lower()
            
            # Kiểm tra nổ file thực thi/nén
            is_dangerous_file = any(content_type.endswith(ext) or final_url.endswith(ext) for ext in [".exe", ".zip", ".scr", ".apk", ".bat", ".vbs", ".sh"])
            
            return {
                "original_url": url,
                "unmasked_destination": final_url,
                "is_redirected": final_url != cleaned_url and final_url.rstrip('/') != cleaned_url.rstrip('/'),
                "is_dangerous_executable_file": is_dangerous_file,
                "is_zero_trust_violation": False,
                "status": "SUCCESS",
                "error_message": ""
            }
    except Exception as e:
        return {
            "original_url": url,
            "unmasked_destination": url,
            "is_redirected": False,
            "is_dangerous_executable_file": False,
            "is_zero_trust_violation": False,
            "status": "TIMEOUT_OR_ERROR",
            "error_message": f"Không thể kết nối giải mã link đích (Timeout 3.0s hoặc máy chủ chối từ): {str(e)}"
        }
