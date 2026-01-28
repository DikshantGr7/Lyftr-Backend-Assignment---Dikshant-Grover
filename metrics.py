from threading import Lock

_lock = Lock()

_metrics = {
    "webhook_requests_total": 0,
    "messages_created_total": 0,
    "messages_duplicate_total": 0,
}

def inc_webhook_requests() -> None:
    with _lock:
        _metrics["webhook_requests_total"] += 1

def inc_messages_created() -> None:
    with _lock:
        _metrics["messages_created_total"] += 1

def inc_messages_duplicate() -> None:
    with _lock:
        _metrics["messages_duplicate_total"] += 1

def get_metrics() -> dict:
    with _lock:
        return dict(_metrics)
