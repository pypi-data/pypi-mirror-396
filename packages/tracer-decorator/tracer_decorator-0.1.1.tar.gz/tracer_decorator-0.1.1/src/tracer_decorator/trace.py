import json
import functools
from datetime import datetime, timezone
from pathlib import Path

TRACE_FILE = Path("/tmp/tracer/python_monitoring.txt")

def trace(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = datetime.now(timezone.utc)
        result = func(*args, **kwargs)
        elapsed = (datetime.now(timezone.utc) - start).total_seconds()
        
        entry = {
            "timestamp": start.isoformat(),
            "function": func.__name__,
            "args": repr(args),
            "kwargs": repr(kwargs),
            "output": repr(result),
            "time_seconds": elapsed,
        }
        
        TRACE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(TRACE_FILE, "a") as f:
            f.write(json.dumps(entry) + "\n")
        
        return result
    return wrapper
