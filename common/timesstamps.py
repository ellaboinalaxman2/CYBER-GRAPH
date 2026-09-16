from datetime import datetime, timezone
from typing import Optional, Union

def get_current_timestamp() -> str:
    """Get current UTC timestamp in ISO format"""
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def format_timestamp(dt: Union[datetime, str]) -> str:
    """Format timestamp for storage"""
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
        except ValueError:
            return dt
    
    if isinstance(dt, datetime):
        return dt.isoformat().replace('+00:00', 'Z')
    
    return str(dt)

def parse_timestamp(timestamp_str: str) -> Optional[datetime]:
    """Parse timestamp string to datetime"""
    try:
        return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
    except ValueError:
        return None

def get_timestamp_diff(start: Union[datetime, str], end: Union[datetime, str]) -> float:
    """Get difference between two timestamps in seconds"""
    if isinstance(start, str):
        start = parse_timestamp(start)
    if isinstance(end, str):
        end = parse_timestamp(end)
    
    if start and end:
        return (end - start).total_seconds()
    
    return 0.0