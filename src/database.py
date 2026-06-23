"""
Scientific Intelligence Engine — Database Layer
Handles SQLite storage for Knowledge Graph, Discovery History, Trend Tracking,
Feedback, and Field Emergence data.
"""

import os
import json
import sqlite3
import datetime
from pathlib import Path

DB_PATH = Path("data") / "scientific_intelligence.db"
DATABASE_URL = os.environ.get("DATABASE_URL")
IS_POSTGRES = DATABASE_URL is not None and DATABASE_URL.startswith("postgres")

if IS_POSTGRES:
    import psycopg2
    import psycopg2.extras

def _connect():
    if IS_POSTGRES:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    else:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        return conn

def get_cursor(conn):
    if IS_POSTGRES:
        return conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    return conn.cursor()

def execute_query(cursor, query: str, params: tuple = ()):
    if IS_POSTGRES:
        # Convert SQLite schema/syntax to Postgres
        query = query.replace("AUTOINCREMENT", "SERIAL")
        
        # Handle SQLite Upsert patterns manually
        if "INSERT OR IGNORE INTO score_history" in query:
            query = query.replace("INSERT OR IGNORE INTO score_history", "INSERT INTO score_history")
            query += " ON CONFLICT (discovery_id, recorded_date) DO NOTHING"
            
        elif "INSERT OR IGNORE INTO alert_history" in query:
            query = query.replace("INSERT OR IGNORE INTO alert_history", "INSERT INTO alert_history")
            query += " ON CONFLICT (rule_id, discovery_id, fired_date) DO NOTHING"
            
        elif "INSERT OR REPLACE INTO field_momentum" in query:
            query = query.replace("INSERT OR REPLACE INTO field_momentum", "INSERT INTO field_momentum")
            query += " ON CONFLICT (field, recorded_date) DO UPDATE SET paper_count=EXCLUDED.paper_count, avg_score=EXCLUDED.avg_score"
            
        elif "INSERT OR REPLACE INTO subscriber_profiles" in query:
            query = query.replace("INSERT OR REPLACE INTO subscriber_profiles", "INSERT INTO subscriber_profiles")
            query += " ON CONFLICT (email) DO UPDATE SET ignored_topics=EXCLUDED.ignored_topics, favorite_fields=EXCLUDED.favorite_fields, feedback_history=EXCLUDED.feedback_history"
            
        # Convert ? to %s
        query = query.replace("?", "%s")
        
    cursor.execute(query, params)

def init_db():
    """Initialize the database schema (idempotent)."""
    conn = _connect()
    cursor = get_cursor(conn)

    # ── Discoveries Table (Primary Entity) ─────────────────────────────────
    execute_query(cursor, """
        CREATE TABLE IF NOT EXISTS discoveries (
            id                 TEXT PRIMARY KEY,
            title              TEXT,
            abstract           TEXT,
            primary_domain     TEXT,
            first_seen_date    TEXT,
            last_seen_date     TEXT,
            significance_score REAL DEFAULT 0.0,
            trend_score        REAL DEFAULT 0.0,
            status             TEXT DEFAULT 'Emerging',
            source_urls        TEXT,
            authors            TEXT,
            source_types       TEXT DEFAULT '[]'
        )
    """)

    # ── Score History Table (powers trend_score) ────────────────────────────
    execute_query(cursor, """
        CREATE TABLE IF NOT EXISTS score_history (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            discovery_id TEXT NOT NULL,
            recorded_date TEXT NOT NULL,
            score        REAL NOT NULL,
            UNIQUE(discovery_id, recorded_date)
        )
    """)

    # ── User Feedback Table ─────────────────────────────────────────────────
    execute_query(cursor, """
        CREATE TABLE IF NOT EXISTS user_feedback (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            discovery_id    TEXT NOT NULL,
            subscriber_email TEXT,
            rating          TEXT NOT NULL,
            recorded_date   TEXT NOT NULL
        )
    """)

    # ── Field Momentum Table (powers Emerging Field Detector) ───────────────
    execute_query(cursor, """
        CREATE TABLE IF NOT EXISTS field_momentum (
            field           TEXT NOT NULL,
            recorded_date   TEXT NOT NULL,
            paper_count     INTEGER DEFAULT 0,
            avg_score       REAL DEFAULT 0.0,
            PRIMARY KEY (field, recorded_date)
        )
    """)

    # ── Subscriber Profiles Table (Personalization) ─────────────────────────
    execute_query(cursor, """
        CREATE TABLE IF NOT EXISTS subscriber_profiles (
            email           TEXT PRIMARY KEY,
            ignored_topics  TEXT DEFAULT '[]',
            favorite_fields TEXT DEFAULT '[]',
            feedback_history TEXT DEFAULT '[]'
        )
    """)

    # ── Knowledge Graph Nodes ───────────────────────────────────────────────
    execute_query(cursor, """
        CREATE TABLE IF NOT EXISTS knowledge_nodes (
            node_id   TEXT PRIMARY KEY,
            node_name TEXT UNIQUE,
            node_type TEXT,
            field     TEXT,
            subfield  TEXT
        )
    """)

    # ── Knowledge Graph Edges ───────────────────────────────────────────────
    execute_query(cursor, """
        CREATE TABLE IF NOT EXISTS knowledge_edges (
            edge_id           TEXT PRIMARY KEY,
            source_node       TEXT,
            target_node       TEXT,
            relationship_type TEXT,
            weight            REAL,
            FOREIGN KEY(source_node) REFERENCES knowledge_nodes(node_id),
            FOREIGN KEY(target_node) REFERENCES knowledge_nodes(node_id)
        )
    """)

    conn.commit()
    conn.close()


# ─────────────────────────────────────────────────────────────────────────────
# LIFECYCLE LOGIC
# Status only ADVANCES — never downgrade Breakthrough → Emerging on a bad day
# ─────────────────────────────────────────────────────────────────────────────

LIFECYCLE_ORDER = ["Emerging", "Growing", "Breakthrough", "Established", "Foundational"]

def _advance_status(current: str, score: float) -> str:
    """Compute new status based on score — but never downgrade."""
    if score > 9.0:
        candidate = "Established"
    elif score > 8.0:
        candidate = "Breakthrough"
    elif score > 6.0:
        candidate = "Growing"
    else:
        candidate = "Emerging"

    # Never downgrade
    current_rank = LIFECYCLE_ORDER.index(current) if current in LIFECYCLE_ORDER else 0
    candidate_rank = LIFECYCLE_ORDER.index(candidate)
    return LIFECYCLE_ORDER[max(current_rank, candidate_rank)]


def _compute_trend_score(cursor, discovery_id: str, today_score: float) -> float:
    """
    Compute velocity: (today_score - oldest_score) / days_since_oldest.
    Returns 0.0 if no history exists or it's day 1.
    """
    today = datetime.date.today()
    execute_query(cursor, 
        "SELECT score, recorded_date FROM score_history WHERE discovery_id=? ORDER BY recorded_date ASC LIMIT 1",
        (discovery_id,)
    )
    row = cursor.fetchone()
    if not row:
        return 0.0
    
    old_score = row["score"]
    old_date = datetime.date.fromisoformat(row["recorded_date"][:10])
    days = max(1, (today - old_date).days)
    
    return round((today_score - old_score) / days, 4)


# ─────────────────────────────────────────────────────────────────────────────
# SAVE DISCOVERIES
# ─────────────────────────────────────────────────────────────────────────────

def save_discoveries(discoveries: list[dict]):
    """Insert or update discoveries with lifecycle tracking and trend velocity."""
    init_db()
    conn = _connect()
    cursor = get_cursor(conn)
    today = datetime.date.today().isoformat()

    for d in discoveries:
        did   = d.get("id")
        title = d.get("title", "")
        if not did or not title:
            continue

        abstract    = d.get("abstract", "")
        domain      = d.get("domain", "")
        score       = float(d.get("scores", {}).get("composite", 0.0))
        urls        = json.dumps([d.get("url", "")] + d.get("cluster_urls", []))
        authors     = json.dumps(d.get("authors", []))
        
        # Aggregate source counts
        sources_list = d.get("sources", [])
        if sources_list:
            from collections import Counter
            counts = Counter([s.get("type", "paper").lower() for s in sources_list])
            source_types = json.dumps(dict(counts))
        else:
            # Fallback
            source_types = json.dumps({"paper": 1})

        # Record today's score into history (for future trend computation)
        execute_query(cursor, 
            "INSERT OR IGNORE INTO score_history (discovery_id, recorded_date, score) VALUES (?,?,?)",
            (did, today, score)
        )

        # Check if discovery already exists
        execute_query(cursor, 
            "SELECT id, status, significance_score FROM discoveries WHERE id=? OR title=?",
            (did, title)
        )
        row = cursor.fetchone()

        if row:
            existing_id   = row["id"]
            current_status= row["status"] or "Emerging"
            new_status    = _advance_status(current_status, score)
            trend         = _compute_trend_score(cursor, existing_id, score)

            execute_query(cursor, """
                UPDATE discoveries
                SET last_seen_date=?, significance_score=?, trend_score=?,
                    status=?, source_urls=?, authors=?, source_types=?
                WHERE id=?
            """, (today, score, trend, new_status, urls, authors, source_types, existing_id))
        else:
            execute_query(cursor, """
                INSERT INTO discoveries
                    (id, title, abstract, primary_domain, first_seen_date, last_seen_date,
                     significance_score, trend_score, status, source_urls, authors, source_types)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            """, (did, title, abstract, domain, today, today, score, 0.0, "Emerging",
                  urls, authors, source_types))

    # ── Save field momentum for Emerging Field Detector ──────────────────
    from collections import defaultdict
    field_groups: dict[str, list[float]] = defaultdict(list)
    for d in discoveries:
        domain = d.get("domain", "Other")
        score  = float(d.get("scores", {}).get("composite", 0.0))
        field_groups[domain].append(score)

    for field, scores in field_groups.items():
        avg  = round(sum(scores) / len(scores), 4)
        count= len(scores)
        execute_query(cursor, """
            INSERT OR REPLACE INTO field_momentum (field, recorded_date, paper_count, avg_score)
            VALUES (?,?,?,?)
        """, (field, today, count, avg))

    conn.commit()
    conn.close()
    print(f"✅ Saved {len(discoveries)} discoveries to Knowledge Base.")


# ─────────────────────────────────────────────────────────────────────────────
# FEEDBACK INGESTION
# ─────────────────────────────────────────────────────────────────────────────

def save_feedback(discovery_id: str, subscriber_email: str, rating: str):
    """Record a user feedback event (called from feedback processing step)."""
    init_db()
    conn = _connect()
    cursor = get_cursor(conn)
    execute_query(cursor, """
        INSERT INTO user_feedback (discovery_id, subscriber_email, rating, recorded_date)
        VALUES (?,?,?,?)
    """, (discovery_id, subscriber_email, rating, datetime.date.today().isoformat()))
    conn.commit()
    conn.close()


def get_feedback_boosted_ids(days: int = 30) -> dict[str, float]:
    """
    Returns {discovery_id: boost_multiplier} based on positive feedback.
    Very Useful = +0.3, Useful = +0.1, Neutral = 0, Not Useful = -0.2
    """
    init_db()
    conn = _connect()
    cursor = get_cursor(conn)
    threshold = (datetime.date.today() - datetime.timedelta(days=days)).isoformat()
    execute_query(cursor, 
        "SELECT discovery_id, rating FROM user_feedback WHERE recorded_date >= ?",
        (threshold,)
    )
    rows = cursor.fetchall()
    conn.close()

    RATING_MAP = {
        "Very Useful": 0.3,
        "Useful":      0.1,
        "Neutral":     0.0,
        "Not Useful": -0.2,
    }
    boosts: dict[str, float] = {}
    for row in rows:
        did  = row["discovery_id"]
        bump = RATING_MAP.get(row["rating"], 0.0)
        boosts[did] = round(boosts.get(did, 0.0) + bump, 3)
    return boosts


# ─────────────────────────────────────────────────────────────────────────────
# SUBSCRIBER PROFILES (Personalization)
# ─────────────────────────────────────────────────────────────────────────────

def get_subscriber_profile(email: str) -> dict:
    init_db()
    conn = _connect()
    cursor = get_cursor(conn)
    execute_query(cursor, "SELECT * FROM subscriber_profiles WHERE email=?", (email,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return {"ignored_topics": [], "favorite_fields": [], "feedback_history": []}
    
    return {
        "ignored_topics": json.loads(row["ignored_topics"]),
        "favorite_fields": json.loads(row["favorite_fields"]),
        "feedback_history": json.loads(row["feedback_history"])
    }

def update_subscriber_profile(email: str, profile_data: dict):
    init_db()
    conn = _connect()
    cursor = get_cursor(conn)
    
    ign = json.dumps(profile_data.get("ignored_topics", []))
    fav = json.dumps(profile_data.get("favorite_fields", []))
    fb  = json.dumps(profile_data.get("feedback_history", []))
    
    execute_query(cursor, """
        INSERT OR REPLACE INTO subscriber_profiles (email, ignored_topics, favorite_fields, feedback_history)
        VALUES (?, ?, ?, ?)
    """, (email, ign, fav, fb))
    
    conn.commit()
    conn.close()

# ─────────────────────────────────────────────────────────────────────────────
# RECENT DISCOVERIES
# ─────────────────────────────────────────────────────────────────────────────

def filter_recent_discoveries(days: int = 7) -> list[dict]:
    """Retrieve discoveries updated recently, ordered by significance."""
    conn = _connect()
    cursor = get_cursor(conn)
    threshold = (datetime.date.today() - datetime.timedelta(days=days)).isoformat()
    execute_query(cursor, 
        "SELECT * FROM discoveries WHERE last_seen_date >= ? ORDER BY significance_score DESC",
        (threshold,)
    )
    rows = cursor.fetchall()
    conn.close()

    results = []
    for r in rows:
        results.append({
            "id":         r["id"],
            "title":      r["title"],
            "abstract":   r["abstract"],
            "domain":     r["primary_domain"],
            "status":     r["status"],
            "trend_score":r["trend_score"],
            "scores":     {"composite": r["significance_score"]},
            "url":        json.loads(r["source_urls"])[0] if r["source_urls"] else "",
            "authors":    json.loads(r["authors"]) if r["authors"] else [],
            "source_types": json.loads(r["source_types"]) if r["source_types"] else [],
        })
    return results


def get_trending_discoveries(top_n: int = 10) -> list[dict]:
    """Return discoveries with the highest positive trend_score (fastest rising)."""
    conn = _connect()
    cursor = get_cursor(conn)
    execute_query(cursor, 
        "SELECT * FROM discoveries WHERE trend_score > 0 ORDER BY trend_score DESC LIMIT ?",
        (top_n,)
    )
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "id":          r["id"],
            "title":       r["title"],
            "domain":      r["primary_domain"],
            "trend_score": r["trend_score"],
            "status":      r["status"],
        }
        for r in rows
    ]


if __name__ == "__main__":
    init_db()
    print("✅ Database initialized successfully.")
