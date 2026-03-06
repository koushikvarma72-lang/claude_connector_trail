from core.config import RATE_LIMIT
from core.metrics import record_invocation, record_rate_limit_hit
from core.rate_limit import is_rate_limited


def guarded_tool(tool_name: str, client_id: str = "global") -> dict | None:
    limited, _remaining = is_rate_limited(RATE_LIMIT, client_id)

    if limited:
        record_rate_limit_hit(tool_name)
        return {
            "error": "Rate limit exceeded",
            "limit": f"{RATE_LIMIT} requests/min",
            "window": "60 seconds",
            "retry_after": "Try again within 60 seconds",
            "tip": "You can change RATE_LIMIT_PER_MIN in your .env to increase the limit",
        }

    record_invocation(tool_name, success=True)
    return None
