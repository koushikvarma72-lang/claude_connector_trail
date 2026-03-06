import threading
from collections import defaultdict
from datetime import datetime

MAX_LOG_SIZE = 500

metrics: dict = {
    "total_invocations": 0,
    "per_tool": defaultdict(int),
    "per_tool_errors": defaultdict(int),
    "rate_limit_hits": 0,
    "invocation_log": [],
}
metrics_lock = threading.Lock()


def record_invocation(tool_name: str, success: bool, error: str | None = None) -> None:
    with metrics_lock:
        metrics["total_invocations"] += 1
        metrics["per_tool"][tool_name] += 1

        if not success:
            metrics["per_tool_errors"][tool_name] += 1

        metrics["invocation_log"].append(
            {
                "tool": tool_name,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "success": success,
                "error": error,
            }
        )

        if len(metrics["invocation_log"]) > MAX_LOG_SIZE:
            metrics["invocation_log"] = metrics["invocation_log"][-MAX_LOG_SIZE:]


def record_rate_limit_hit(tool_name: str) -> None:
    with metrics_lock:
        metrics["rate_limit_hits"] += 1
        metrics["invocation_log"].append(
            {
                "tool": tool_name,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "success": False,
                "error": "rate_limit_exceeded",
            }
        )


def get_metrics_snapshot(rate_limit: int) -> dict:
    with metrics_lock:
        return {
            "rate_limit_config": f"{rate_limit} requests/min (sliding window)",
            "total_invocations": metrics["total_invocations"],
            "rate_limit_hits": metrics["rate_limit_hits"],
            "per_tool_calls": dict(metrics["per_tool"]),
            "per_tool_errors": dict(metrics["per_tool_errors"]),
            "recent_invocations": metrics["invocation_log"][-10:],
            "note": "Metrics reset on server restart. Use Redis for persistence.",
        }


def reset_metrics() -> dict:
    with metrics_lock:
        metrics["total_invocations"] = 0
        metrics["per_tool"] = defaultdict(int)
        metrics["per_tool_errors"] = defaultdict(int)
        metrics["rate_limit_hits"] = 0
        metrics["invocation_log"] = []

    return {
        "message": "Metrics reset successfully.",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
