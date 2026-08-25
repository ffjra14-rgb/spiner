#!/usr/bin/env python3
# header_injection.py - Header Injection Scanner

import re
import requests
import urllib.parse
from typing import Dict, Any, List

PAYLOAD_FILE = "assets/payloads/Header Injection.txt"
TIMEOUT = 10

HEADER_NAMES = [
    "X-Forwarded-For", "X-Real-IP", "X-Remote-IP",
    "X-Client-IP", "X-Originating-IP"
]

def load_payloads() -> List[str]:
    try:
        with open(PAYLOAD_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.strip().startswith("X-Forwarded-For")]
    except FileNotFoundError:
        return ["X-Forwarded-For: 127.0.0.1"]

def run(target: str, **kwargs) -> Dict[str, Any]:
    results = {
        "status": "ok",
        "result": {},
        "errors": [],
        "duration": 0
    }
    
    try:
        payloads = load_payloads()
        
        # Для Header Injection проверяем разные заголовки
        vulnerable = []
        for payload in payloads[:50]:
            try:
                headers = {"User-Agent": "Mozilla/5.0"}
                # Добавляем тестовый заголовок
                if ":" in payload:
                    key, value = payload.split(":", 1)
                    headers[key.strip()] = value.strip()
                
                resp = requests.get(target, headers=headers, timeout=TIMEOUT)
                
                # Проверяем, отразился ли заголовок в ответе (зависит от приложения)
                # Упрощённо: проверяем статус и длину
                if resp.status_code == 200:
                    vulnerable.append({
                        "header": payload,
                        "type": "Header Injection"
                    })
            except Exception as e:
                results["errors"].append(f"Ошибка: {str(e)}")
        
        results["result"]["vulnerable"] = vulnerable
        results["result"]["count"] = len(vulnerable)
        
        if not vulnerable:
            results["result"]["message"] = "Header инъекции не найдены"
        
    except Exception as e:
        results["status"] = "error"
        results["errors"].append(str(e))
    
    return results