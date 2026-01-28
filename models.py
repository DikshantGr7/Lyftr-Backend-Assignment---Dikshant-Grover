import sqlite3
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
import re

# Pydantic Models for Input (Webhook) 

class WebhookRequest(BaseModel):
    message_id: str = Field(..., min_length=1)
    from_msisdn: str = Field(..., alias="from")
    to_msisdn: str = Field(..., alias="to")
    ts: str
    text: Optional[str] = Field(None, max_length=4096)

    @field_validator("from_msisdn", "to_msisdn")
    @classmethod
    def validate_msisdn(cls, v: str) -> str:
        if not re.match(r"^\+\d+$", v):
            raise ValueError("Must start with '+' followed by digits only")
        return v

    @field_validator("ts")
    @classmethod
    def validate_timestamp(cls, v: str) -> str:
        if not v.endswith("Z"):
            raise ValueError("Timestamp must end with 'Z'")
        return v

class MessageData(BaseModel):
    message_id: str
    from_msisdn: str = Field(..., alias="from")
    to_msisdn: str = Field(..., alias="to")
    ts: str
    text: Optional[str]

class MessagesResponse(BaseModel):
    data: List[MessageData]
    total: int
    limit: int
    offset: int

class SenderStats(BaseModel):
    from_msisdn: str = Field(..., alias="from")
    count: int

class StatsResponse(BaseModel):
    total_messages: int
    senders_count: int
    messages_per_sender: List[SenderStats]
    first_message_ts: Optional[str]
    last_message_ts: Optional[str]

# SQLite Schema Initialization 

def init_db(conn: sqlite3.Connection) -> None:
    conn.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        message_id TEXT PRIMARY KEY,
        from_msisdn TEXT NOT NULL,
        to_msisdn   TEXT NOT NULL,
        ts          TEXT NOT NULL,
        text        TEXT,
        created_at  TEXT NOT NULL
    )
    """)
    conn.commit()
