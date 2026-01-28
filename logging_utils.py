import time
import json
import logging
import uuid
from datetime import datetime
from fastapi import Request

class StructuredJSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "ts": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
        }

        if hasattr(record, "extra_info") and isinstance(record.extra_info, dict):
            log_record.update(record.extra_info)

        return json.dumps(log_record)

logger = logging.getLogger("app_logger")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(StructuredJSONFormatter())
    logger.addHandler(handler)

logger.propagate = False

async def structured_log_middleware(request: Request, call_next):
    start_time = time.time()

    request_id = str(uuid.uuid4())
    request.state.log_extra = {
        "request_id": request_id
    }

    response = await call_next(request)

    latency_ms = (time.time() - start_time) * 1000

    log_data = {
        "request_id": request_id,
        "method": request.method,
        "path": request.url.path,
        "status": response.status_code,
        "latency_ms": round(latency_ms, 2),
    }

    if hasattr(request.state, "log_extra"):
        log_data.update(request.state.log_extra)

    logger.info(
        "request_completed",
        extra={"extra_info": log_data},
    )

    return response
