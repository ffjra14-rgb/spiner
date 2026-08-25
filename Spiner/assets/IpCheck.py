#!/usr/bin/env python3
# IpCheck.py - IP Geolocation

import requests
import time
from typing import Dict, Any

def get_geolocation(ip: str) -> Dict[str, Any]:
    try:
        # ip-api.com - бесплатный, 45 запросов/мин
        url = f"http://ip-api.com/json/{ip}"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        
        if data.get("status") == "success":
            return {
                "country": data.get("country", ""),
                "country_code": data.get("countryCode", ""),
                "region": data.get("regionName", ""),
                "city": data.get("city", ""),
                "isp": data.get("isp", ""),
                "org": data.get("org", ""),
                "as": data.get("as", ""),
                "lat": data.get("lat", 0),
                "lon": data.get("lon", 0),
                "timezone": data.get("timezone", ""),
                "zip": data.get("zip", ""),
                "status": "ok"
            }
        else:
            return {"status": "error", "message": data.get("message", "Unknown error")}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def is_private_ip(ip: str) -> bool:
    """Проверка на частный IP"""
    private_prefixes = [
        "127.", "192.168.", "10.", 
        "172.16.", "172.17.", "172.18.", "172.19.",
        "172.20.", "172.21.", "172.22.", "172.23.",
        "172.24.", "172.25.", "172.26.", "172.27.",
        "172.28.", "172.29.", "172.30.", "172.31.",
        "169.254."
    ]
    for prefix in private_prefixes:
        if ip.startswith(prefix):
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
        ip = target.strip()
        
        # Проверка на частный IP
        if is_private_ip(ip):
            results["result"] = {
                "status": "private",
                "message": f"IP {ip} является частным (локальным)",
                "ip": ip
            }
            return results
        
        # Получаем геоданные
        geo_data = get_geolocation(ip)
        
        if geo_data.get("status") == "ok":
            results["result"] = {
                "ip": ip,
                "country": geo_data.get("country", "Неизвестно"),
                "country_code": geo_data.get("country_code", ""),
                "region": geo_data.get("region", "Неизвестно"),
                "city": geo_data.get("city", "Неизвестно"),
                "isp": geo_data.get("isp", "Неизвестно"),
                "organization": geo_data.get("org", "Неизвестно"),
                "as": geo_data.get("as", "Неизвестно"),
                "coordinates": f"{geo_data.get('lat', 0)}, {geo_data.get('lon', 0)}",
                "timezone": geo_data.get("timezone", "Неизвестно"),
                "zip": geo_data.get("zip", ""),
                "status": "ok"
            }
        else:
            results["status"] = "error"
            results["result"] = {
                "ip": ip,
                "status": "error",
                "message": geo_data.get("message", "Не удалось получить данные")
            }
            results["errors"].append(geo_data.get("message", "Unknown error"))
        
    except Exception as e:
        results["status"] = "error"
        results["errors"].append(str(e))
        results["result"] = {"status": "error", "message": str(e)}
    
    return results