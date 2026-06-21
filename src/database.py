"""
Scientific Intelligence Engine — Database Layer
Handles SQLite storage for Knowledge Graph, Discovery History, Trend Tracking,
Feedback, and Field Emergence data.
"""

import json
import sqlite3
import datetime
from pathlib import Path

DB_PATH = Path("data") / "scientific_intelligence.db"


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the SQLite database schema (idempotent)."""
    conn = _connect()
    cursor = conn.cursor()

    # ── Discoveries Table (Primary Entity) ─────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS discoveries (
            id                 TEXT PRIMARY KEY,
            title              TEXT,
            abstract           TEXT,
            primary_domain     TEXT,
            first_seen_date    TEXT,
            last_seen_date     TEXT,
            significance_score REAL DEFAULT 0.0,
            trend_score        REAL DEFAULT 0.0,   -- velocity: score change per day
            status             TEXT DEFAULT 'Emerging',
            source_urls        TEXT,               -- JSON array
            authors            TEXT,               -- JSON array
            source_types       TEXT DEFAULT '[]'   -- JSON array: ["paper","patent","grant"]
        )
    """)

    # ── Score History Table (powers trend_score) ────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS score_history (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            discovery_id TEXT NOT NULL,
            recorded_date TEXT NOT NULL,
            score        REAL NOT NULL,
            UNIQUE(discovery_id, recorded_date)
        )
    """)

    # ── User Feedback Table ─────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_feedback (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            discovery_id    TEXT NOT NULL,
            subscriber_email TEXT,
            rating          TEXT NOT NULL,     -- Very Useful / Useful / Neutral / Not Useful
            recorded_date   TEXT NOT NULL
        )
    """)

    # ── Field Momentum Table (powers Emerging Field Detector) ───────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS field_momentum (
            field           TEXT NOT NULL,
            recorded_date   TEXT NOT NULL,
            paper_count     INTEGER DEFAULT 0,
            avg_score       REAL DEFAULT 0.0,
            PRIMARY KEY (field, recorded_date)
        )
    """)

    # ── Knowledge Graph Nodes ───────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_nodes (
            node_id   TEXT PRIMARY KEY,
            node_name TEXT UNIQUE,
            node_type TEXT,
            field     TEXT,
            subfield  TEXT
        )
    """)

    # ── Knowledge Graph Edges ───────────────────────────────────────────────
    cursor.execute("""
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


def _compute_trend_score(cursor: sqlite3.Cursor, discovery_id: str, today_score: float) -> float:
    """
    Compute velocity: (today_score - score_7_days_ago) / 7.
    Returns 0.0 if no history exists yet.
    """
    week_ago = (datetime.date.today() - datetime.timedelta(days=7)).isoformat()
    cursor.execute(
        "SELECT score FROM score_history WHERE discovery_id=? AND recorded_date<=? ORDER BY recorded_date DESC LIMIT 1",
        (discovery_id, week_ago)
    )
    row = cursor.fetchone()
    if not row:
        return 0.0
    old_score = row["score"]
    days = 7
    return round((today_score - old_score) / days, 4)


# ─────────────────────────────────────────────────────────────────────────────
# SAVE DISCOVERIES
# ─────────────────────────────────────────────────────────────────────────────

def save_discoveries(discoveries: list[dict]):
    """Insert or update discoveries with lifecycle tracking and trend velocity."""
    init_db()
    conn = _connect()
    cursor = conn.cursor()
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
        source_types= json.dumps(list(set(d.get("source_types", ["paper"]))))

        # Record today's score into history (for future trend computation)
        cursor.execute(
            "INSERT OR IGNORE INTO score_history (discovery_id, recorded_date, score) VALUES (?,?,?)",
            (did, today, score)
        )

        # Check if discovery already exists
        cursor.execute(
            "SELECT id, status, significance_score FROM discoveries WHERE id=? OR title=?",
            (did, title)
        )
        row = cursor.fetchone()

        if row:
            existing_id   = row["id"]
            current_status= row["status"] or "Emerging"
            new_status    = _advance_status(current_status, score)
            trend         = _compute_trend_score(cursor, existing_id, score)

            cursor.execute("""
                UPDATE discoveries
                SET last_seen_date=?, significance_score=?, trend_score=?,
                    status=?, source_urls=?, authors=?, source_types=?
                WHERE id=?
            """, (today, score, trend, new_status, urls, authors, source_types, existing_id))
        else:
            cursor.execute("""
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
        cursor.execute("""
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
    conn.execute("""
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
    threshold = (datetime.date.today() - datetime.timedelta(days=days)).isoformat()
    rows = conn.execute(
        "SELECT discovery_id, rating FROM user_feedback WHERE recorded_date >= ?",
        (threshold,)
    ).fetchall()
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
# FILTER & RETRIEVE
# ─────────────────────────────────────────────────────────────────────────────

def filter_recent_discoveries(days: int = 7) -> list[dict]:
    """Retrieve discoveries updated recently, ordered by significance."""
    conn = _connect()
    threshold = (datetime.date.today() - datetime.timedelta(days=days)).isoformat()
    rows = conn.execute(
        "SELECT * FROM discoveries WHERE last_seen_date >= ? ORDER BY significance_score DESC",
        (threshold,)
    ).fetchall()
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
    rows = conn.execute(
        "SELECT * FROM discoveries WHERE trend_score > 0 ORDER BY trend_score DESC LIMIT ?",
        (top_n,)
    ).fetchall()
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
