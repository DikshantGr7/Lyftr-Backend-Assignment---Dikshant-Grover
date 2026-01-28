import sqlite3
from datetime import datetime
from typing import List, Tuple, Optional, Dict, Any


# Insert (Webhook)

def insert_message(
    conn: sqlite3.Connection,
    message_id: str,
    from_msisdn: str,
    to_msisdn: str,
    ts: str,
    text: Optional[str],
) -> str:
    """
    Insert a message exactly once.
    Returns:
        "created"   -> first insert
        "duplicate" -> message_id already exists
    """
    try:
        
        conn.execute(
            """
            INSERT INTO messages (
                message_id, from_msisdn, to_msisdn, ts, text, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                message_id,
                from_msisdn,
                to_msisdn,
                ts,
                text,
                datetime.utcnow().isoformat() + "Z",
            ),
        )
        conn.commit()
        return "created"
    except sqlite3.IntegrityError:

        return "duplicate"

# Query (GET /messages)

def get_messages(
    conn: sqlite3.Connection,
    limit: int,
    offset: int,
    from_msisdn: Optional[str] = None,
    since: Optional[str] = None,
    q: Optional[str] = None,
) -> Tuple[List[Dict[str, Any]], int]:
    """
    Returns:
        data  -> list of dictionaries (for easier JSON serialization)
        total -> total rows matching filters ignoring limit/offset
    """
    filters = []
    params: List = []

    if from_msisdn:
        filters.append("from_msisdn = ?")
        params.append(from_msisdn)

    if since:
        filters.append("ts >= ?")
        params.append(since)

    if q:

        filters.append("text LIKE ?")
        params.append(f"%{q}%")

    where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""

    count_sql = f"SELECT COUNT(*) FROM messages {where_clause}"
    total = conn.execute(count_sql, params).fetchone()[0]

    data_sql = f"""
        SELECT message_id, from_msisdn, to_msisdn, ts, text
        FROM messages
        {where_clause}
        ORDER BY ts ASC, message_id ASC
        LIMIT ? OFFSET ?
    """

    rows = conn.execute(data_sql, params + [limit, offset]).fetchall()

    data = []
    for row in rows:
        d = dict(row)
        d["from"] = d.pop("from_msisdn")
        d["to"] = d.pop("to_msisdn")
        data.append(d)

    return data, total

# Query (GET /stats)
def get_stats(conn: sqlite3.Connection) -> Dict[str, Any]:
    """
    Compute message analytics with top 10 senders.
    """
    total_messages = conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
    senders_count = conn.execute("SELECT COUNT(DISTINCT from_msisdn) FROM messages").fetchone()[0]

    sender_rows = conn.execute(
        """
        SELECT from_msisdn as 'from', COUNT(*) as count
        FROM messages
        GROUP BY from_msisdn
        ORDER BY count DESC
        LIMIT 10
        """
    ).fetchall()

    first_last = conn.execute("SELECT MIN(ts), MAX(ts) FROM messages").fetchone()

    return {
        "total_messages": total_messages,
        "senders_count": senders_count,
        "messages_per_sender": [dict(r) for r in sender_rows],
        "first_message_ts": first_last[0], 
        "last_message_ts": first_last[1],  
    }