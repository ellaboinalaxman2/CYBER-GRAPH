# app/utils/timestamps.py
from datetime import datetime

def iso_format(dt: datetime) -> str:
    return dt.isoformat()