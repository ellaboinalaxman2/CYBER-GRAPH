# app/utils/hashing.py
import hashlib
import json

def generate_sha256(data: dict) -> str:
    json_str = json.dumps(data, sort_keys=True)
    return hashlib.sha256(json_str.encode()).hexdigest()