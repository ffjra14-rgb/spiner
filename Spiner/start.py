#!/usr/bin/env python3
# start.py - Главный мультитул (Spiner by @Fugufo)

import os
import sys
import time
import importlib
import logging
import platform
import socket
import subprocess
import psutil
from datetime import datetime
from typing import Optional, Dict, Any

# ==================== КОНФИГУРАЦИЯ ====================
LOG_DIR = "logs"
PAYLOAD_DIR = "assets/payloads"
MODULES_DIR = "assets"

# ==================== ЦВЕТА ====================
C = {
    "red": "\033[91m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "blue": "\033[94m",
    "magenta": "\033[95m",
    "cyan": "\033[96m",
    "white": "\033[97m",
    "reset": "\033[0m",
    "bold": "\033[1m",
}

def col(text, color="white", bold=False):
    b = C["bold"] if bold else ""
    return f"{b}{C.get(color, C['white'])}{text}{C['reset']}"

# ==================== СИСТЕМНАЯ ИНФОРМАЦИЯ ====================
def get_local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def get_public_ip() -> str:
    try:
        import requests
        return requests.get("https://api.ipify.org", timeout=5).text.strip()
    except:
        return "Не определен"

def get_cpu_usage() -> str:
    try:
        return f"{psutil.cpu_percent(interval=0.5)}%"
    except:
        return "N/A"

def get_system_info() -> Dict[str, str]:
    info = {
        "os": platform.system(),
        "release": platform.release(),
        "arch": platform.machine(),
        "cores": str(psutil.cpu_count(logical=True)),
        "hostname": platform.node(),
        "ram_total": f"{round(psutil.virtual_memory().total / (1024**3), 1)} GB",
        "ram_used": f"{round(psutil.virtual_memory().used / (1024**3), 1)} GB",
        "ram_percent": f"{psutil.virtual_memory().percent}%",
    }
    return info

# ==================== БАННЕР ====================
BANNER = """
                    d8,                          
                   `8P                           
                                                 
 .d888b,?88,.d88b,  88b  88bd88b  d8888b  88bd88b
 ?8b,   `?88'  ?88  88P  88P' ?8bd8b_,dP  88P'  `
   `?8b   88b  d8P d88  d88   88P88b     d88     
`?888P'   888888P'd88' d88'   88b`?888P'd88'     
          88P'                                   
         d88                                     
         ?8P
"""

def print_banner():
    os.system("clear" if os.name == "posix" else "cls")
    
    local_ip = get_local_ip()
    public_ip = get_public_ip()
    cpu_usage = get_cpu_usage()
    sys_info = get_system_info()
    
    print(col(BANNER, "cyan", True))
    print(col("=" * 60, "green", True))
    print(col(f"  Spiner by @Fugufo", "yellow", True))
    print(col(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}", "yellow"))
    print(col("  " + "-" * 56, "magenta"))
    print(col(f"  Локальный IP: {local_ip}", "cyan"))
    print(col(f"  Публичный IP: {public_ip}", "cyan"))
    print(col(f"  CPU: {cpu_usage}  |  RAM: {sys_info['ram_used']} / {sys_info['ram_total']} ({sys_info['ram_percent']})", "cyan"))
    print(col(f"  ОС: {sys_info['os']} {sys_info['release']}  |  Архитектура: {sys_info['arch']}", "cyan"))
    print(col(f"  Хост: {sys_info['hostname']}  |  Ядер: {sys_info['cores']}", "cyan"))
    print(col("  " + "-" * 56, "magenta"))
    print(col("  MultiTool v2.0 | 22 модуля", "magenta"))
    print(col("=" * 60, "green", True))

# ==================== ЛОГГЕР ====================
def setup_logger():
    os.makedirs(LOG_DIR, exist_ok=True)
    log_file = os.path.join(LOG_DIR, f"spiner_{datetime.now().strftime('%Y%m%d')}.log")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("Spiner")

logger = setup_logger()

# ==================== МЕНЮ ====================
MENU = {
    "1": {"name": "XSS Scanner", "module": "xss", "desc": "Поиск XSS уязвимостей"},
    "2": {"name": "SQL Injection Scanner", "module": "sql", "desc": "Поиск SQLi уязвимостей"},
    "3": {"name": "NoSQL Scanner", "module": "nosql", "desc": "Поиск NoSQL уязвимостей"},
    "4": {"name": "DoS Attack", "module": "dos", "desc": "HTTP Flood / Slowloris"},
    "5": {"name": "Phone Validator", "module": "PhoneValid", "desc": "Проверка номера"},
    "6": {"name": "Gmail Validator", "module": "GmailValid", "desc": "Проверка почты"},
    "7": {"name": "IP Geolocation", "module": "IpCheck", "desc": "Геолокация по IP"},
    "8": {"name": "Command Injection", "module": "command_injection", "desc": "Command Injection"},
    "9": {"name": "CRLF Injection", "module": "crlf_injection", "desc": "CRLF Injection"},
    "10": {"name": "Code Injection", "module": "code_injection", "desc": "Code Injection"},
    "11": {"name": "LDAP Injection", "module": "ldap_injection", "desc": "LDAP Injection"},
    "12": {"name": "ORM Injection", "module": "orm_injection", "desc": "ORM Injection"},
    "13": {"name": "Email Injection", "module": "email_injection", "desc": "Email Injection"},
    "14": {"name": "Header Injection", "module": "header_injection", "desc": "Header Injection"},
    "15": {"name": "Log Injection", "module": "log_injection", "desc": "Log Injection"},
    "16": {"name": "XSLT Injection", "module": "xslt_injection", "desc": "XSLT Injection"},
    "17": {"name": "XXE Scanner", "module": "xxe", "desc": "XXE уязвимости"},
    "18": {"name": "GraphQL Injection", "module": "graphql_injection", "desc": "GraphQL Injection"},
    "19": {"name": "SSTI Scanner", "module": "ssti", "desc": "SSTI уязвимости"},
    "20": {"name": "XPath Injection", "module": "xpath_injection", "desc": "XPath Injection"},
    "21": {"name": "SSRF Scanner", "module": "ssrf", "desc": "SSRF уязвимости"},
    "22": {"name": "HTML Injection", "module": "html_injection", "desc": "HTML Injection"},
    "23": {"name": "Proxy Manager", "module": None, "desc": "Управление прокси"},
    "24": {"name": "About", "module": None, "desc": "О программе"},
    "25": {"name": "Exit", "module": None, "desc": "Выход"},
}

def show_menu():
    print(col("\n" + "=" * 60, "green"))
    print(col("  МЕНЮ МОДУЛЕЙ", "yellow", True))
    print(col("=" * 60, "green"))
    
    items = list(MENU.items())
    for i in range(0, len(items), 2):
        left = items[i]
        right = items[i+1] if i+1 < len(items) else None
        
        left_str = col(f"[{left[0]}] {left[1]['name']}", "cyan")
        if right:
            right_str = col(f"[{right[0]}] {right[1]['name']}", "cyan")
            print(f"  {left_str:<35} {right_str}")
        else:
            print(f"  {left_str}")
    
    print(col("=" * 60, "green"))
    print()

# ==================== PROXY MANAGER ====================
def proxy_manager_menu():
    """Меню управления прокси"""
    try:
        from assets.proxy_manager import proxy_manager
    except ImportError:
        print(col("[!] Модуль proxy_manager не найден. Создайте assets/proxy_manager.py", "red"))
        input(col("Нажмите Enter...", "cyan"))
        return
    
    while True:
        print(col("\n=== УПРАВЛЕНИЕ ПРОКСИ ===", "yellow", True))
        print(col(f"Всего прокси: {len(proxy_manager.proxies)}", "cyan"))
        print(col(f"Рабочих: {len(proxy_manager.working_proxies)}", "green" if proxy_manager.working_proxies else "red"))
        print()
        print("[1] Проверить все прокси")
        print("[2] Показать список прокси")
        print("[3] Добавить прокси")
        print("[4] Удалить прокси")
        print("[5] Очистить список")
        print("[6] Назад")
        
        choice = input(col("Выберите: ", "magenta")).strip()
        
        if choice == "1":
            print(col("\n[+] Проверка прокси...", "yellow"))
            results = proxy_manager.check_all_proxies()
            working = 0
            for r in results:
                status = col("✅ РАБОЧИЙ", "green") if r["working"] else col("❌ МЁРТВЫЙ", "red")
                print(f"  {r['proxy']} -> {status}")
                if r["working"]:
                    working += 1
            print(col(f"\nИтого: {working}/{len(results)} рабочих", "cyan"))
        
        elif choice == "2":
            print(col("\n=== СПИСОК ПРОКСИ ===", "yellow"))
            if not proxy_manager.proxies:
                print(col("  Список пуст", "red"))
            else:
                for i, p in enumerate(proxy_manager.proxies, 1):
                    print(f"  {i}. {p}")
        
        elif choice == "3":
            proxy_str = input(col("Введите прокси (host:port или protocol://host:port): ", "cyan")).strip()
            if proxy_str:
                proxy_manager.add_proxy(proxy_str)
                print(col(f"[+] Прокси {proxy_str} добавлен", "green"))
        
        elif choice == "4":
            if not proxy_manager.proxies:
                print(col("[!] Список прокси пуст", "red"))
            else:
                for i, p in enumerate(proxy_manager.proxies, 1):
                    print(f"  {i}. {p}")
                idx = input(col("Введите номер прокси для удаления: ", "cyan")).strip()
                if idx.isdigit() and 1 <= int(idx) <= len(proxy_manager.proxies):
                    removed = proxy_manager.proxies[int(idx)-1]
                    proxy_manager.remove_proxy(removed)
                    print(col(f"[+] Прокси {removed} удалён", "yellow"))
        
        elif choice == "5":
            if not proxy_manager.proxies:
                print(col("[!] Список уже пуст", "red"))
            else:
                confirm = input(col("Удалить все прокси? (y/n): ", "red")).strip().lower()
                if confirm == "y":
                    proxy_manager.proxies = []
                    proxy_manager.working_proxies = []
                    proxy_manager.save_proxies()
                    print(col("[+] Все прокси удалены", "red"))
        
        elif choice == "6":
            break
        
        input(col("\nНажмите Enter...", "cyan"))

# ==================== ABOUT ====================
def show_about():
    print(col("\n=== ABOUT ===", "yellow", True))
    print(col("Spiner MultiTool v2.0", "green"))
    print(col("Автор: @Fugufo", "green"))
    print(col("Модулей: 22", "green"))
    print(col("Функции: XSS, SQLi, NoSQL, DoS, Phone, Email, IP,", "green"))
    print(col("  Command, CRLF, Code, LDAP, ORM, Email, Header,", "green"))
    print(col("  Log, XSLT, XXE, GraphQL, SSTI, XPath, SSRF, HTML", "green"))
    print(col("Дата создания: 2025", "green"))

# ==================== ДИСПЕТЧЕР ====================
def dispatch(choice: str, target: Optional[str] = None, proxy: Optional[Dict[str, str]] = None, **kwargs) -> Dict[str, Any]:
    if choice not in MENU:
        return {"status": "error", "result": "Неверный выбор", "errors": ["Invalid choice"]}
    
    menu_item = MENU[choice]
    module_name = menu_item["module"]
    
    if module_name is None:
        return {"status": "info", "result": f"Выбран пункт: {menu_item['name']}", "errors": []}
    
    try:
        module = importlib.import_module(f"assets.{module_name}")
        if not hasattr(module, "run"):
            return {"status": "error", "result": f"Модуль {module_name} не имеет функции run()", "errors": ["Missing run()"]}
    except ImportError as e:
        logger.error(f"Ошибка импорта {module_name}: {e}")
        return {"status": "error", "result": f"Не удалось загрузить модуль {module_name}", "errors": [str(e)]}
    
    try:
        start_time = time.time()
        result = module.run(target, proxy=proxy, **kwargs)
        result["duration"] = round(time.time() - start_time, 2)
        logger.info(f"{module_name} -> {target} -> {result.get('status', 'unknown')}")
        return result
    except Exception as e:
        logger.error(f"Ошибка выполнения {module_name}: {e}")
        return {"status": "error", "result": f"Ошибка: {str(e)}", "errors": [str(e)]}

def format_result(result: Dict[str, Any]) -> str:
    if result.get("status") == "error":
        return col(f"[ОШИБКА] {result.get('result', 'Unknown error')}", "red", True)
    if result.get("status") == "info":
        return col(result.get("result", ""), "yellow")
    
    output = []
    data = result.get("result", {})
    if isinstance(data, dict):
        for key, value in data.items():
            if key in ["status", "errors", "duration"]:
                continue
            if isinstance(value, list):
                output.append(col(f"{key}:", "cyan", True))
                for item in value:
                    if isinstance(item, dict):
                        output.append(f"  - {item.get('type', 'Unknown')}: {item.get('payload', item)}")
                    else:
                        output.append(f"  - {item}")
            elif isinstance(value, bool):
                output.append(col(f"{key}:", "cyan", True) + f" {'Да' if value else 'Нет'}")
            else:
                output.append(col(f"{key}:", "cyan", True) + f" {value}")
    elif isinstance(data, str):
        output.append(data)
    else:
        output.append(str(data))
    
    if result.get("duration"):
        output.append(col(f"\nВремя выполнения: {result['duration']} сек.", "yellow"))
    
    return "\n".join(output)

# ==================== ВЫБОР ПРОКСИ ====================
def choose_proxy() -> Optional[Dict[str, str]]:
    """Интерактивный выбор прокси"""
    print(col("\nИспользовать прокси?", "yellow"))
    print("[1] Без прокси")
    print("[2] Случайный прокси из списка")
    print("[3] Проверить и выбрать рабочий прокси")
    print("[4] Ввести прокси вручную")
    
    choice = input(col("Выберите (1-4): ", "cyan")).strip()
    
    if choice == "1":
        return None
    elif choice == "2":
        try:
            from assets.proxy_manager import proxy_manager
            proxy = proxy_manager.get_random_proxy()
            if proxy:
                print(col(f"[+] Используется прокси: {proxy}", "green"))
                return proxy
            else:
                print(col("[!] Нет прокси в списке", "red"))
                return None
        except ImportError:
            print(col("[!] Модуль proxy_manager не найден", "red"))
            return None
    elif choice == "3":
        try:
            from assets.proxy_manager import proxy_manager
            print(col("[+] Поиск рабочего прокси...", "yellow"))
            proxy = proxy_manager.get_first_working()
            if proxy:
                print(col(f"[+] Найден рабочий прокси: {proxy}", "green"))
                return proxy
            else:
                print(col("[!] Рабочий прокси не найден", "red"))
                return None
        except ImportError:
            print(col("[!] Модуль proxy_manager не найден", "red"))
            return None
    elif choice == "4":
        proxy_str = input(col("Введите прокси (host:port или protocol://host:port): ", "cyan")).strip()
        if proxy_str:
            try:
                from assets.proxy_manager import ProxyManager
                pm = ProxyManager()
                parsed = pm._parse_proxy(proxy_str)
                if parsed:
                    print(col(f"[+] Используется прокси: {parsed}", "green"))
                    return parsed
                else:
                    print(col("[!] Неверный формат прокси", "red"))
                    return None
            except ImportError:
                # Простой парсинг
                if ":" in proxy_str:
                    if not proxy_str.startswith(("http://", "https://", "socks4://", "socks5://")):
                        proxy_str = f"http://{proxy_str}"
                    return {"http": proxy_str, "https": proxy_str}
                print(col("[!] Неверный формат прокси", "red"))
                return None
    else:
        return None

# ==================== ГЛАВНЫЙ ЦИКЛ ====================
def main():
    while True:
        print_banner()
        show_menu()
        
        choice = input(col("Выберите пункт (1-25): ", "magenta", True)).strip()
        
        if choice == "25":
            print(col("Выход...", "red", True))
            logger.info("Выход из программы")
            break
        
        if choice == "24":
            show_about()
            input(col("\nНажмите Enter для продолжения...", "cyan"))
            continue
        
        if choice == "23":
            proxy_manager_menu()
            continue
        
        if choice not in MENU:
            print(col("Неверный выбор. Попробуйте снова.", "red"))
            time.sleep(1)
            continue
        
        menu_item = MENU[choice]
        
        if menu_item["module"] is None:
            continue
        
        print(col(f"\n=== {menu_item['name']} ===", "yellow", True))
        
        # Запрос цели
        if choice in ["1", "2", "3", "4", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22"]:
            target = input(col("Введите URL (http://...): ", "cyan")).strip()
        elif choice == "5":
            target = input(col("Введите номер телефона: ", "cyan")).strip()
        elif choice == "6":
            target = input(col("Введите email: ", "cyan")).strip()
        elif choice == "7":
            target = input(col("Введите IP-адрес: ", "cyan")).strip()
        else:
            target = ""
        
        if not target:
            print(col("Цель не указана.", "red"))
            time.sleep(1)
            continue
        
        # Выбор прокси (для сетевых модулей)
        proxy = None
        if choice in ["1", "2", "3", "4", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22"]:
            proxy = choose_proxy()
            if proxy is None and choice != "4":
                # Если прокси не выбран, продолжаем без него
                pass
        
        # Дополнительные параметры для DoS
        kwargs = {}
        if choice == "4":
            print(col("\nВыберите тип атаки:", "yellow"))
            print("[1] HTTP Flood (GET)")
            print("[2] Slowloris")
            attack_type = input(col("Выберите (1/2): ", "cyan")).strip()
            kwargs["attack_type"] = "http" if attack_type == "1" else "slowloris"
            
            threads = input(col("Количество потоков (по умолчанию 50): ", "cyan")).strip()
            kwargs["threads"] = int(threads) if threads.isdigit() else 50
            
            duration = input(col("Длительность в секундах (0 = бесконечно): ", "cyan")).strip()
            kwargs["duration"] = int(duration) if duration.isdigit() else 0
        
        print(col("\n[+] Запуск...", "green"))
        result = dispatch(choice, target, proxy=proxy, **kwargs)
        
        print(col("\n[РЕЗУЛЬТАТ]", "yellow", True))
        print(format_result(result))
        
        if result.get("errors"):
            print(col("\n[ОШИБКИ]", "red", True))
            for err in result["errors"]:
                print(f"  - {err}")
        
        input(col("\nНажмите Enter для продолжения...", "cyan"))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(col("\nПрервано.", "red"))
        sys.exit(0)