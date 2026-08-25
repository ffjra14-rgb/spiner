#!/usr/bin/env python3
# graphql_injection.py - GraphQL Injection Scanner

import re
import json
import requests
import urllib.parse
from typing import Dict, Any, List

PAYLOAD_FILE = "assets/payloads/GraphQL Injection.txt"
TIMEOUT = 10

GRAPHQL_ERRORS = [
    "$ne", "$gt", "$regex", "$where",
    "MongoError", "CastError",
    "GraphQLError", "ValidationError"
]

def load_payloads() -> List[str]:
    try:
        with open(PAYLOAD_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return ['{"username": {"$ne": null}}']

def detect_graphql_error(response_text: str) -> bool:
    for pattern in GRAPHQL_ERRORS:
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
        
        # GraphQL часто принимает JSON в POST
        vulnerable = []
        for payload in payloads[:30]:
            try:
                # Пробуем отправить как query parameter
                test_url = f"{target}?query={urllib.parse.quote(payload)}"
                resp = requests.get(test_url, timeout=TIMEOUT)
                
                if detect_graphql_error(resp.text) or "graphql" in resp.text.lower():
                    vulnerable.append({
                        "payload": payload,
                        "type": "GraphQL Injection (GET)"
                    })
                    break
                
                # Пробуем POST
                headers = {"Content-Type": "application/json"}
                data = {"query": payload}
                resp = requests.post(target, json=data, headers=headers, timeout=TIMEOUT)
                
                if detect_graphql_error(resp.text) or "graphql" in resp.text.lower():
                    vulnerable.append({
                        "payload": payload,
                        "type": "GraphQL Injection (POST)"
                    })
                    break
                    
            except Exception as e:
                results["errors"].append(f"Ошибка: {str(e)}")
        
        results["result"]["vulnerable"] = vulnerable
        results["result"]["count"] = len(vulnerable)
        
        if not vulnerable:
            results["result"]["message"] = "GraphQL инъекции не найдены"
        
    except Exception as e:
        results["status"] = "error"
        results["errors"].append(str(e))
    
    return results