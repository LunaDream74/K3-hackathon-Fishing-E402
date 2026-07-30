import json
import re
from urllib.parse import urlparse
from pathlib import Path
from typing import Dict, Any, List

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
        # Bỏ 'www.' nếu có để chuẩn hóa so sánh
        if hostname.startswith("www."):
            hostname = hostname[4:]
        return hostname.lower()
    except Exception:
        return ""

def is_raw_ip(hostname: str) -> bool:
    """
    Kiểm tra xem hostname có phải là địa chỉ IP tĩnh (thường dùng trong phishing trái phép) không.
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

def extract_all_urls(text: str) -> List[str]:
    """
    Sử dụng biểu thức chính quy (Regex) để trích xuất toàn bộ đường link trong văn bản email.
    Bao gồm cả link http://, https://, ftp:// hoặc domain.extension (như vinai-verify.tk/login).
    """
    url_pattern = re.compile(
        r'(?:(?:https?|ftp)://)?'
        r'(?:[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b|'
        r'(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))'
        r'(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)',
        re.IGNORECASE
    )
    
    matches = url_pattern.findall(text)
    # Lọc bỏ các từ thông thông thường có dấu chấm rớt vào ranh giới ngữ pháp nếu cần
    valid_urls = []
    for m in matches:
        m_clean = m.rstrip(".,;!?:')\"")
        # Đảm bảo có chứa ít nhất 1 dấu chấm hoặc là http/https
        if "." in m_clean or m_clean.startswith("http"):
            valid_urls.append(m_clean)
            
    # Xoá trùng lặp nhưng giữ thứ tự xuất hiện
    return list(dict.fromkeys(valid_urls))
