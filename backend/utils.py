import os
import json
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional

class Colors:
    """Warna untuk terminal"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

def print_banner():
    """Banner keren untuk terminal"""
    banner = f"""
{Colors.PURPLE}╔══════════════════════════════════════════════════════════════╗
║                                                                  ║
║   {Colors.RED}███████╗██╗      {Colors.WHITE} ██████╗██╗███████╗███╗   ██╗ ██████╗ ██████╗ {Colors.PURPLE}║
║   {Colors.RED}██╔════╝██║     {Colors.WHITE} ██╔════╝██║██╔════╝████╗  ██║██╔════╝██╔═══██╗{Colors.PURPLE}║
║   {Colors.RED}█████╗  ██║     {Colors.WHITE} ██║     ██║█████╗  ██╔██╗ ██║██║     ██║   ██║{Colors.PURPLE}║
║   {Colors.RED}██╔══╝  ██║     {Colors.WHITE} ██║     ██║██╔══╝  ██║╚██╗██║██║     ██║   ██║{Colors.PURPLE}║
║   {Colors.RED}███████╗███████╗{Colors.WHITE} ╚██████╗██║███████╗██║ ╚████║╚██████╗╚██████╔╝{Colors.PURPLE}║
║   {Colors.RED}╚══════╝╚══════╝{Colors.WHITE}  ╚═════╝╚═╝╚══════╝╚═╝  ╚═══╝ ╚═════╝ ╚═════╝ {Colors.PURPLE}║
║                                                                  ║
║              {Colors.CYAN}🔥 STALKER PRO - Instagram & TikTok OSINT 🔥{Colors.PURPLE}       ║
║                    {Colors.YELLOW}Made for El Manco{Colors.PURPLE}                             ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝{Colors.RESET}
    """
    print(banner)

def generate_id(text: str) -> str:
    """Generate unique ID dari text"""
    timestamp = datetime.now().isoformat()
    return hashlib.md5(f"{text}{timestamp}".encode()).hexdigest()[:12]

def format_number(num: int) -> str:
    """Format angka dengan K/M suffix"""
    if num >= 1000000:
        return f"{num/1000000:.1f}M"
    elif num >= 1000:
        return f"{num/1000:.1f}K"
    return str(num)

def ensure_dir(path: str):
    """Pastikan direktori ada"""
    os.makedirs(path, exist_ok=True)

def save_json(filepath: str, data: Any):
    """Simpan data ke JSON"""
    ensure_dir(os.path.dirname(filepath))
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_json(filepath: str, default: Any = None) -> Any:
    """Load data dari JSON"""
    if not os.path.exists(filepath):
        return default if default is not None else []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return default if default is not None else []
