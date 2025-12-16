import os
import re
from datetime import datetime, timezone

def resolve_env_value(value, default_env_var):
    if value is None:
        return os.environ.get(default_env_var)
    if re.match('^[A-Z][A-Z0-9_]*$', value):
        return os.environ.get(value, value)
    return value

def truncate_to_limit(items, limit, size_fn):
    result = []
    total = 0
    for item in items:
        size = size_fn(item)
        if total + size > limit:
            break
        result.append(item)
        total += size
    return result

def get_byte_size(text):
    if text is None:
        return 0
    return len(text.encode('utf-8'))

def iso_timestamp(dt=None):
    if dt is None:
        dt = datetime.now(timezone.utc)
    return dt.isoformat()

def extract_patterns(text, pattern):
    if not text:
        return []
    return re.findall(pattern, text)