#!/usr/bin/env python3
# nosql.py - NoSQL Injection Scanner

import re
import json
import requests
import urllib.parse
from typing import Dict, Any, List

PAYLOAD_FILE = "assets/payloads/NoSql'шники.txt"
TIMEOUT = 10

# Признаки NoSQL-ошибок
NOSQL_ERRORS = [
    "MongoError",
    "CastError",
    "$ne",
    "$gt",
    "$regex",
    "MongoDB",
    "ObjectId",
    "unrecognized",
    "unknown operator",
    "Mongo"
]

def load_payloads() -> List[str]:
    try:
        with open(PAYLOAD_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.strip().startswith("--")]
    except FileNotFoundError:
        return ['{"$ne": null}', '{"$gt": ""}']

def detect_nosql_error(response_text: str) -> bool:
    for pattern in NOSQL_ERRORS:
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
                # Для NoSQL иногда нужно кодировать JSON
                try:
                    # Если payload похож на JSON - попробуем отправить как есть
                    test_payload = payload
                    new_params = {k: v[0] if k != param else test_payload for k, v in params.items()}
                    new_query = urllib.parse.urlencode(new_params)
                    test_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{new_query}"
                    
                    resp = requests.get(test_url, timeout=TIMEOUT)
                    if detect_nosql_error(resp.text):
                        vulnerable.append({
                            "param": param,
                            "payload": payload,
                            "type": "Error-based"
                        })
                        break
                except Exception as e:
                    results["errors"].append(f"Ошибка для {param}: {str(e)}")
        
        results["result"]["vulnerable"] = vulnerable
        results["result"]["count"] = len(vulnerable)
        
        if not vulnerable:
            results["result"]["message"] = "NoSQL инъекции не найдены"
        
    except Exception as e:
        results["status"] = "error"
        results["errors"].append(str(e))
    
    return results