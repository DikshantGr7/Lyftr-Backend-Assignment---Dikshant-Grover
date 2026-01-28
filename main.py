import hmac
import hashlib
import json
import sqlite3
import logging

from fastapi import FastAPI, Request, HTTPException
from datetime import datetime

from config import DB_PATH, WEBHOOK_SECRET, LOG_LEVEL
from models import (
    WebhookRequest,
    MessagesResponse,
    MessageData,
    StatsResponse,
    init_db,
)
from storage import insert_message, get_messages, get_stats
from logging_utils import structured_log_middleware
from metrics import (
    inc_webhook_requests,
    inc_messages_created,
    inc_messages_duplicate,
    get_metrics,
)

logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger("lyftr-backend")

app = FastAPI(title="Lyftr AI Backend Assignment")
app.middleware("http")(structured_log_middleware)

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
conn.row_factory = sqlite3.Row
init_db(conn)

def verify_hmac_signature(raw_body: bytes, signature: str) -> None:
    expected = hmac.new(
        WEBHOOK_SECRET.encode(),
        raw_body,
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(expected, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

@app.get("/health/live")
def health_live():
    return {"status": "ok"}

@app.get("/health/ready")
def health_ready():
    try:
        conn.execute("SELECT 1 FROM messages LIMIT 1")
        return {"status": "ok"}
    except Exception:
        raise HTTPException(status_code=503, detail="Database not ready")

@app.post("/webhook")
async def webhook(request: Request):
    inc_webhook_requests()

    raw_body = await request.body()
    signature = request.headers.get("X-Signature")

    if not signature:
        raise HTTPException(status_code=401, detail="Missing signature")

    verify_hmac_signature(raw_body, signature)

    try:
        payload = json.loads(raw_body)
        data = WebhookRequest(**payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    status = insert_message(
        conn=conn,
        message_id=data.message_id,
        from_msisdn=data.from_msisdn,
        to_msisdn=data.to_msisdn,
        ts=data.ts,
        text=data.text,
    )

    if status == "created":
        inc_messages_created()
    else:
        inc_messages_duplicate()

    request.state.log_extra.update({
        "message_id": data.message_id,
        "from": data.from_msisdn,
        "insert_status": status,
    })

    return {"status": "ok"}

@app.get(
    "/messages",
    response_model=MessagesResponse,
    response_model_by_alias=True,
)
def list_messages(
    limit: int = 50,
    offset: int = 0,
    from_msisdn: str | None = None,
    since: str | None = None,
    q: str | None = None,
):
    data, total = get_messages(
        conn=conn,
        limit=limit,
        offset=offset,
        from_msisdn=from_msisdn,
        since=since,
        q=q,
    )

    messages = [MessageData(**row) for row in data]

    return {
        "data": messages,
        "total": total,
        "limit": limit,
        "offset": offset,
    }

@app.get(
    "/stats",
    response_model=StatsResponse,
    response_model_by_alias=True,
)
def stats():
    return get_stats(conn)

@app.get("/metrics")
def metrics():
    return get_metrics()
