"""
Scientific Intelligence Engine — Database Layer
Handles SQLite storage for Knowledge Graph and Discovery History.
"""

import sqlite3
import datetime
from pathlib import Path

DB_PATH = Path("data") / "scientific_intelligence.db"

def init_db():
    """Initialize the SQLite database schema."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    # Discoveries Table (Primary Entity)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS discoveries (
            id TEXT PRIMARY KEY,
            title TEXT,
            abstract TEXT,
            primary_domain TEXT,
            first_seen_date TEXT,
            last_seen_date TEXT,
            significance_score REAL,
            trend_score REAL,
            status TEXT,          -- Emerging, Growing, Breakthrough, Established, Foundational
            source_urls TEXT,     -- JSON array of URLs
            authors TEXT          -- JSON array of authors
        )
    """)

    # Knowledge Graph Nodes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_nodes (
            node_id TEXT PRIMARY KEY,
            node_name TEXT UNIQUE,
            node_type TEXT,       -- Technology, Field, Concept, Dataset, etc.
            field TEXT,
            subfield TEXT
        )
    """)

    # Knowledge Graph Edges
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_edges (
            edge_id TEXT PRIMARY KEY,
            source_node TEXT,
            target_node TEXT,
            relationship_type TEXT, -- enables, influences, bounds, etc.
            weight REAL,
            FOREIGN KEY(source_node) REFERENCES knowledge_nodes(node_id),
            FOREIGN KEY(target_node) REFERENCES knowledge_nodes(node_id)
        )
    """)

    conn.commit()
    conn.close()

def save_discoveries(discoveries: list[dict]):
    """Insert or update discoveries in the database."""
    init_db()
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    today = datetime.date.today().isoformat()

    for d in discoveries:
        import json
        did = d.get("id")
        title = d.get("title", "")
        abstract = d.get("abstract", "")
        domain = d.get("domain", "")
        score = d.get("scores", {}).get("composite", 0.0)
        
        # Check if exists (simple duplicate detection by ID or exact title)
        # In a full system, this would use semantic similarity.
        cursor.execute("SELECT id, first_seen_date FROM discoveries WHERE id=? OR title=?", (did, title))
        row = cursor.fetchone()
        
        status = "Emerging"
        if score > 8.0:
            status = "Breakthrough"
        elif score > 6.0:
            status = "Growing"

        urls = json.dumps([d.get("url", "")] + d.get("cluster_urls", []))
        authors = json.dumps(d.get("authors", []))

        if row:
            # Update existing discovery
            existing_id, first_seen = row
            cursor.execute("""
                UPDATE discoveries 
                SET last_seen_date=?, significance_score=?, status=?, source_urls=?, authors=?
                WHERE id=?
            """, (today, score, status, urls, authors, existing_id))
        else:
            # Insert new discovery
            cursor.execute("""
                INSERT INTO discoveries (id, title, abstract, primary_domain, first_seen_date, last_seen_date, significance_score, trend_score, status, source_urls, authors)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (did, title, abstract, domain, today, today, score, 0.0, status, urls, authors))

    conn.commit()
    conn.close()

def filter_recent_discoveries(days: int = 7) -> list[dict]:
    """Retrieve discoveries updated recently."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    threshold = (datetime.date.today() - datetime.timedelta(days=days)).isoformat()
    cursor.execute("SELECT * FROM discoveries WHERE last_seen_date >= ? ORDER BY significance_score DESC", (threshold,))
    rows = cursor.fetchall()
    conn.close()
    
    import json
    results = []
    for r in rows:
        results.append({
            "id": r["id"],
            "title": r["title"],
            "abstract": r["abstract"],
            "domain": r["primary_domain"],
            "status": r["status"],
            "scores": {"composite": r["significance_score"]},
            "url": json.loads(r["source_urls"])[0] if r["source_urls"] else "",
            "authors": json.loads(r["authors"]) if r["authors"] else []
        })
    return results

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
