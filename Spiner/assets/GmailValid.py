#!/usr/bin/env python3
# GmailValid.py - Email Validator

import re
import socket
import smtplib
import dns.resolver
from typing import Dict, Any, List

TIMEOUT = 5

def validate_syntax(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def get_mx_records(domain: str) -> List[str]:
    try:
        records = dns.resolver.resolve(domain, 'MX')
        return [str(record.exchange).rstrip('.') for record in records]
    except:
        return []

def smtp_verify(email: str, mx_server: str) -> bool:
    try:
        domain = email.split('@')[1]
        server = smtplib.SMTP(mx_server, 25, timeout=TIMEOUT)
        server.ehlo()
        server.mail('')
        code, message = server.rcpt(email)
        server.quit()
        return code == 250
    except:
        return False

def run(target: str, **kwargs) -> Dict[str, Any]:
    results = {
        "status": "ok",
        "result": {},
        "errors": [],
        "duration": 0
    }
    
    try:
        email = target.strip().lower()
        
        # 1. Синтаксис
        syntax_valid = validate_syntax(email)
        results["result"]["syntax_valid"] = syntax_valid
        
        if not syntax_valid:
            results["result"]["message"] = "Неверный синтаксис email"
            results["result"]["mailbox_exists"] = False
            return results
        
        # 2. MX-записи
        domain = email.split('@')[1]
        mx_records = get_mx_records(domain)
        results["result"]["mx_records"] = mx_records
        results["result"]["domain_exists"] = len(mx_records) > 0
        
        if not mx_records:
            results["result"]["mailbox_exists"] = False
            results["result"]["message"] = "Домен не имеет MX-записей"
            return results
        
        # 3. SMTP-верификация
        mailbox_exists = False
        for mx in mx_records[:2]:  # Проверяем первые 2 MX
            if smtp_verify(email, mx):
                mailbox_exists = True
                break
        
        results["result"]["mailbox_exists"] = mailbox_exists
        
        if mailbox_exists:
            results["result"]["message"] = "Email валиден и ящик существует"
        else:
            results["result"]["message"] = "Email синтаксически верен, но ящик не удалось подтвердить (возможно, защита от спама)"
        
        # Определяем провайдера
        if "gmail.com" in domain:
            provider = "Gmail"
        elif "yandex" in domain:
            provider = "Yandex"
        elif "mail.ru" in domain:
            provider = "Mail.ru"
        elif "outlook" in domain or "hotmail" in domain:
            provider = "Microsoft"
        else:
            provider = "Другой"
        
        results["result"]["provider"] = provider
        
    except Exception as e:
        results["status"] = "error"
        results["errors"].append(str(e))
    
    return results