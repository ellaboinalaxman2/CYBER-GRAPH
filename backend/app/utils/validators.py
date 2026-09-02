# app/utils/validators.py
import re

def is_valid_ip(ip: str) -> bool:
    pattern = r"^(\d{1,3}\.){3}\d{1,3}$"
    return re.match(pattern, ip) is not None