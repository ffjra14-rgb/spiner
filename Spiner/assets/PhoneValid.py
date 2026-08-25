#!/usr/bin/env python3
# PhoneValid.py - Phone Validator

import re
import requests
from typing import Dict, Any

# Локальная база операторов (Россия, Украина, Казахстан, Перу)
OPERATORS = {
    "ru": {
        "МТС": ["910", "911", "912", "913", "914", "915", "916", "917", "918", "919"],
        "Мегафон": ["920", "921", "922", "923", "924", "925", "926", "927", "928", "929"],
        "Билайн": ["903", "905", "906", "909", "960", "961", "962", "963", "964", "965"],
        "Tele2": ["900", "901", "902", "904", "908", "950", "951", "952", "953", "954"],
        "Yota": ["999"]
    },
    "ua": {
        "Киевстар": ["67", "68", "96", "97", "98"],
        "Vodafone": ["50", "66", "95", "99"],
        "Lifecell": ["63", "93"]
    },
    "kz": {
        "Beeline": ["701", "702", "703", "705", "707", "708", "709"],
        "Kcell": ["701", "702", "703", "705", "707", "708", "709"],
        "Tele2": ["700", "705", "707", "708", "709"]
    },
    "pe": {
        "Claro": ["9", "5"],
        "Movistar": ["1", "2"],
        "Bitel": ["3", "4"],
        "Entel": ["7", "8"]
    }
}

# Номера API (можно заполнить, если есть ключи)
NUMVERIFY_KEY = ""  # Получить на numverify.com

def validate_phone_public(phone: str) -> Dict[str, Any]:
    """Проверка через публичные API (без ключа)"""
    try:
        # api.veriphone.com - бесплатный (но ограничен)
        url = f"https://api.veriphone.com/v1/verify?phone={phone}"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if data.get("status") == "success":
            return {
                "valid": data.get("phone_valid", False),
                "country": data.get("country_code", ""),
                "operator": data.get("carrier", ""),
                "line_type": data.get("line_type", ""),
                "region": ""
            }
    except:
        pass
    return None

def validate_phone_local(phone: str) -> Dict[str, Any]:
    """Локальная валидация по маске"""
    # Очищаем номер
    cleaned = re.sub(r'[\s\-\(\)\+]', '', phone)
    
    if not cleaned.isdigit():
        return {"valid": False, "error": "Номер содержит нецифровые символы"}
    
    # Определяем страну по длине и префиксу
    if cleaned.startswith("7") and len(cleaned) == 11:
        country = "ru"
        code = cleaned[1:4]
    elif cleaned.startswith("38") and len(cleaned) == 12:
        country = "ua"
        code = cleaned[2:4]
    elif cleaned.startswith("77") and len(cleaned) == 11:
        country = "kz"
        code = cleaned[1:4]
    elif cleaned.startswith("51") and len(cleaned) == 10:
        country = "pe"
        code = cleaned[3:4]
    else:
        return {"valid": False, "error": "Неизвестный формат номера"}
    
    # Ищем оператора
    operator = "Неизвестно"
    for op, codes in OPERATORS.get(country, {}).items():
        if code in codes:
            operator = op
            break
    
    return {
        "valid": True,
        "country": country.upper(),
        "operator": operator,
        "line_type": "Мобильный" if len(cleaned) >= 10 else "Стационарный",
        "region": "Не определено"
    }

def run(target: str, **kwargs) -> Dict[str, Any]:
    results = {
        "status": "ok",
        "result": {},
        "errors": [],
        "duration": 0
    }
    
    try:
        # Сначала пробуем через API
        api_result = validate_phone_public(target)
        if api_result:
            results["result"] = api_result
            return results
        
        # Если API не работает - локальная проверка
        local_result = validate_phone_local(target)
        results["result"] = local_result
        
        if not local_result.get("valid"):
            results["status"] = "warning"
            results["errors"].append(local_result.get("error", "Номер невалиден"))
        
    except Exception as e:
        results["status"] = "error"
        results["errors"].append(str(e))
    
    return results