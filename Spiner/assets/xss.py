#!/usr/bin/env python3
# xss.py - XSS Scanner

import re
import requests
import urllib.parse
from typing import Dict, Any, List
from bs4 import BeautifulSoup

PAYLOAD_FILE = "assets/payloads/Xss'шки.txt"
TIMEOUT = 10

def load_payloads() -> List[str]:
    try:
        with open(PAYLOAD_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.strip().startswith("--")]
    except FileNotFoundError:
        return ["<script>alert(1)</script>", "<img src=x onerror=alert(1)>"]

def detect_reflection(response_text: str, payload: str) -> bool:
    # Проверяем отражение пейлоада в ответе
    return payload in response_text

def run(target: str, **kwargs) -> Dict[str, Any]:
    """
    Проверка XSS уязвимостей (Reflected)
    """
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
            for payload in payloads[:50]:  # Ограничим для скорости
                # Формируем новый URL
                new_params = {k: v[0] if k != param else payload for k, v in params.items()}
                new_query = urllib.parse.urlencode(new_params)
                test_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{new_query}"
                
                try:
                    resp = requests.get(test_url, timeout=TIMEOUT)
                    if detect_reflection(resp.text, payload):
                        vulnerable.append({
                            "param": param,
                            "payload": payload,
                            "url": test_url
                        })
                        break
                except Exception as e:
                    results["errors"].append(f"Ошибка для {test_url}: {str(e)}")
        
        results["result"]["vulnerable"] = vulnerable
        results["result"]["count"] = len(vulnerable)
        
        if not vulnerable:
            results["result"]["message"] = "XSS не найдены"
        
    except Exception as e:
        results["status"] = "error"
        results["errors"].append(str(e))
    
    return results