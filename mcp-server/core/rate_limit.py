import threading
import time
from collections import defaultdict

call_log: dict[str, list[float]] = defaultdict(list)
call_lock = threading.Lock()


def is_rate_limited(rate_limit: int, client_id: str = "global") -> tuple[bool, int]:
    now = time.time()
    window_start = now - 60

    with call_lock:
        call_log[client_id] = [t for t in call_log[client_id] if t > window_start]
        count = len(call_log[client_id])

        if count >= rate_limit:
            return True, 0

        call_log[client_id].append(now)
        return False, rate_limit - count - 1
