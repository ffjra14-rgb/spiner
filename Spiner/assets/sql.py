#!/usr/bin/env python3
# sql.py - SQL Injection Scanner

import re
import requests
import urllib.parse
from typing import Dict, Any, List

PAYLOAD_FILE = "assets/payloads/Sql'шки.txt"
TIMEOUT = 10

# Признаки SQL-ошибок
SQL_ERRORS = [
    "SQL syntax",
    "mysql_fetch",
    "Unclosed quotation mark",
    "You have an error in your SQL",
    "Warning: mysql",
    "PostgreSQL",
    "ORA-",
    "Microsoft OLE DB",
    "SQLite",
    "syntax error",
    "unclosed string",
    "quoted string not properly terminated"
]

def load_payloads() -> List[str]:
    try:
        with open(PAYLOAD_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.strip().startswith("--")]
    except FileNotFoundError:
        return ["' OR '1'='1", "' OR 1=1 --"]

def detect_sql_error(response_text: str) -> bool:
    for pattern in SQL_ERRORS:
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
            for payload in payloads[:30]:  # Ограничим для скорости
                new_params = {k: v[0] if k != param else payload for k, v in params.items()}
                new_query = urllib.parse.urlencode(new_params)
                test_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{new_query}"
                
                try:
                    resp = requests.get(test_url, timeout=TIMEOUT)
                    if detect_sql_error(resp.text):
                        vulnerable.append({
                            "param": param,
                            "payload": payload,
                            "type": "Error-based"
                        })
                        break
                except Exception as e:
                    results["errors"].append(f"Ошибка для {test_url}: {str(e)}")
        
        results["result"]["vulnerable"] = vulnerable
        results["result"]["count"] = len(vulnerable)
        
        if not vulnerable:
            results["result"]["message"] = "SQLi не найдены"
        
    except Exception as e:
        results["status"] = "error"
        results["errors"].append(str(e))
    
    return results