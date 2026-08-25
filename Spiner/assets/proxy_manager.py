#!/usr/bin/env python3
# proxy_manager.py - Менеджер прокси с проверкой

import os
import random
import requests
from typing import List, Optional, Dict, Any

class ProxyManager:
    def __init__(self, proxy_file: str = None):
        if proxy_file is None:
            # Ищем proxies.txt в папке payloads
            possible_paths = [
                "assets/payloads/proxies.txt",
                os.path.join(os.path.dirname(__file__), "payloads", "proxies.txt"),
                os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "payloads", "proxies.txt"),
                "proxies.txt",  # fallback
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    proxy_file = path
                    break
            else:
                # Создаём в assets/payloads/
                payloads_dir = os.path.join(os.path.dirname(__file__), "payloads")
                os.makedirs(payloads_dir, exist_ok=True)
                proxy_file = os.path.join(payloads_dir, "proxies.txt")
                # Если файла нет — создаём пустой
                if not os.path.exists(proxy_file):
                    with open(proxy_file, "w", encoding="utf-8") as f:
                        f.write("# Список прокси для Spiner MultiTool\n")
                        f.write("# Формат: host:port или protocol://host:port\n")
                        f.write("# Пример:\n")
                        f.write("# 192.168.1.1:8080\n")
                        f.write("# http://user:pass@host:port\n")
                        f.write("# socks5://host:1080\n")
        
        self.proxy_file = proxy_file
        self.proxies = []
        self.working_proxies = []
        self.current_index = 0
        self.load_proxies()
    
    def load_proxies(self) -> None:
        """Загружает прокси из файла"""
        try:
            if os.path.exists(self.proxy_file):
                with open(self.proxy_file, "r", encoding="utf-8") as f:
                    self.proxies = [line.strip() for line in f if line.strip() and not line.startswith("#")]
            else:
                self.proxies = []
                print(f"[!] Файл {self.proxy_file} не найден. Создан пустой файл.")
        except Exception as e:
            print(f"[!] Ошибка загрузки прокси: {e}")
            self.proxies = []
    
    def save_proxies(self) -> None:
        """Сохраняет прокси в файл"""
        try:
            # Сохраняем только строки (без протокола, для удобства)
            to_save = []
            for p in self.proxies:
                if isinstance(p, dict):
                    url = p.get("http", "")
                    if url:
                        to_save.append(url.replace("http://", "").replace("https://", ""))
                else:
                    to_save.append(p)
            
            with open(self.proxy_file, "w", encoding="utf-8") as f:
                f.write("# Список прокси для Spiner MultiTool\n")
                f.write("# Формат: host:port или protocol://host:port\n")
                f.write("# Добавляйте каждый прокси с новой строки\n\n")
                for p in to_save:
                    if p:
                        f.write(f"{p}\n")
        except Exception as e:
            print(f"[!] Ошибка сохранения прокси: {e}")
    
    def add_proxy(self, proxy_str: str) -> None:
        """Добавляет прокси в список"""
        proxy_str = proxy_str.strip()
        if proxy_str and proxy_str not in self.proxies:
            self.proxies.append(proxy_str)
            self.save_proxies()
            # Удаляем из working_proxies, если был
            if proxy_str in self.working_proxies:
                self.working_proxies.remove(proxy_str)
    
    def remove_proxy(self, proxy_str: str) -> None:
        """Удаляет прокси из списка"""
        if proxy_str in self.proxies:
            self.proxies.remove(proxy_str)
            self.save_proxies()
        if proxy_str in self.working_proxies:
            self.working_proxies.remove(proxy_str)
    
    def get_next_proxy(self) -> Optional[Dict[str, str]]:
        """Возвращает следующий прокси в формате requests"""
        if not self.proxies:
            return None
        
        proxy = self.proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxies)
        return self._parse_proxy(proxy)
    
    def get_random_proxy(self) -> Optional[Dict[str, str]]:
        """Возвращает случайный прокси"""
        if not self.proxies:
            return None
        proxy = random.choice(self.proxies)
        return self._parse_proxy(proxy)
    
    def _parse_proxy(self, proxy_str: str) -> Optional[Dict[str, str]]:
        """Парсит строку прокси в формат requests"""
        if not proxy_str:
            return None
        
        proxy_str = proxy_str.strip()
        
        # Если уже в формате словаря — возвращаем как есть
        if isinstance(proxy_str, dict):
            return proxy_str
        
        # Если нет протокола — добавляем http://
        if not proxy_str.startswith(("http://", "https://", "socks4://", "socks5://")):
            if ":" in proxy_str:
                proxy_str = f"http://{proxy_str}"
            else:
                return None
        
        return {"http": proxy_str, "https": proxy_str}
    
    def check_proxy(self, proxy_str: str, timeout: int = 5) -> bool:
        """Проверяет работоспособность прокси"""
        try:
            proxy = self._parse_proxy(proxy_str)
            if not proxy:
                return False
            test_url = "http://httpbin.org/ip"
            resp = requests.get(test_url, proxies=proxy, timeout=timeout)
            return resp.status_code == 200
        except:
            return False
    
    def check_all_proxies(self, timeout: int = 5) -> List[Dict[str, Any]]:
        """Проверяет все прокси и возвращает статус каждого"""
        results = []
        self.working_proxies = []
        
        for proxy_str in self.proxies:
            is_working = self.check_proxy(proxy_str, timeout)
            results.append({
                "proxy": proxy_str,
                "working": is_working
            })
            if is_working:
                self.working_proxies.append(proxy_str)
        
        return results
    
    def get_working_proxies(self, timeout: int = 5) -> List[str]:
        """Возвращает список рабочих прокси"""
        self.working_proxies = []
        for proxy_str in self.proxies:
            if self.check_proxy(proxy_str, timeout):
                self.working_proxies.append(proxy_str)
        return self.working_proxies
    
    def get_first_working(self, timeout: int = 5) -> Optional[Dict[str, str]]:
        """Возвращает первый рабочий прокси"""
        for proxy_str in self.proxies:
            if self.check_proxy(proxy_str, timeout):
                return self._parse_proxy(proxy_str)
        return None
    
    def get_random_working(self, timeout: int = 5) -> Optional[Dict[str, str]]:
        """Возвращает случайный рабочий прокси"""
        working = self.get_working_proxies(timeout)
        if not working:
            return None
        proxy_str = random.choice(working)
        return self._parse_proxy(proxy_str)
    
    def stats(self) -> Dict[str, int]:
        """Возвращает статистику по прокси"""
        return {
            "total": len(self.proxies),
            "working": len(self.working_proxies)
        }

# Глобальный экземпляр
proxy_manager = ProxyManager()