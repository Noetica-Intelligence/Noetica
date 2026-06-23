"""
Scientific Intelligence Engine — Emerging Field Detector (C12)
Identifies new fields forming by detecting:
  1. Unusual vocabulary appearing in multiple unrelated domains simultaneously
  2. A sharp increase in paper count + avg score for a domain over 14–30 days
  3. Cross-domain clustering: papers from two normally-separate fields
     start citing common concepts

Reads from the field_momentum table in the database (written by save_discoveries).
"""

import datetime
from pathlib import Path
from collections import defaultdict

from database import _connect, get_cursor, execute_query

# ─────────────────────────────────────────────────────────────────────────────
# KNOWN CROSS-DOMAIN CONVERGENCES (seeds for the detector)
# These are field-pairs that, when both accelerate simultaneously, signal
# a new interdisciplinary field forming.
# ─────────────────────────────────────────────────────────────────────────────

CONVERGENCE_SIGNALS: list[dict] = [
    {
        "name":    "AI Drug Discovery",
        "fields":  ["AI & Machine Learning", "Bioinformatics", "Medicine"],
        "keywords":["drug discovery", "molecular generation", "virtual screening", "ADMET"],
    },
    {
        "name":    "Protein Language Models",
        "fields":  ["AI & Machine Learning", "Structural Biology", "Bioinformatics"],
        "keywords":["protein language", "ESM", "ProGen", "protein design"],
    },
    {
        "name":    "Quantum Machine Learning",
        "fields":  ["Quantum Computing", "AI & Machine Learning", "Statistics"],
        "keywords":["quantum neural", "variational circuit", "quantum ML"],
    },
    {
        "name":    "Computational Chronobiology",
        "fields":  ["Circadian Biology", "Bioinformatics", "Systems Biology"],
        "keywords":["circadian", "CLOCK gene", "BMAL1", "chronotherapy"],
    },
    {
        "name":    "Foundation Models for Science",
        "fields":  ["AI & Machine Learning", "Physics", "Biology", "Chemistry"],
        "keywords":["scientific foundation model", "universal model", "science transformer"],
    },
    {
        "name":    "AI-Assisted Mathematics",
        "fields":  ["Pure Mathematics", "AI & Machine Learning", "Computer Science"],
        "keywords":["theorem proving", "Lean", "Coq", "formal proof", "AI math"],
    },
    {
        "name":    "Longevity Science",
        "fields":  ["Medicine", "Biology", "Systems Biology"],
        "keywords":["aging", "longevity", "senescence", "telomere", "epigenetic clock"],
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# CORE DETECTOR
# ─────────────────────────────────────────────────────────────────────────────

def _load_field_momentum(days: int = 30) -> dict[str, list[dict]]:
    """
    Load field_momentum records from the DB for the last N days.
    Returns { field: [{"date": ..., "count": ..., "avg_score": ...}, ...] }
    """
    conn = _connect()
    cursor = get_cursor(conn)
    threshold = (datetime.date.today() - datetime.timedelta(days=days)).isoformat()
    
    try:
        execute_query(cursor, 
            "SELECT * FROM field_momentum WHERE recorded_date >= ? ORDER BY recorded_date ASC",
            (threshold,)
        )
        rows = cursor.fetchall()
    except Exception:
        # Table might not exist yet if DB is fresh
        rows = []
    
    conn.close()

    result: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        result[r["field"]].append({
            "date":      r["recorded_date"],
            "count":     r["paper_count"],
            "avg_score": r["avg_score"],
        })
    return dict(result)


def detect_momentum_surges(
    days: int = 14,
    min_surge_ratio: float = 1.5,
    min_papers: int = 3,
) -> list[dict]:
    """
    Detect fields where paper count OR avg_score has surged compared
    to the prior period.

    surge_ratio = recent_avg_count / historical_avg_count
    Returns a list of surge events sorted by surge magnitude.
    """
    momentum = _load_field_momentum(days=days * 2)
    today    = datetime.date.today()
    cutoff   = (today - datetime.timedelta(days=days)).isoformat()

    surges = []
    for field, records in momentum.items():
        recent   = [r for r in records if r["date"] >= cutoff]
        historic = [r for r in records if r["date"] <  cutoff]

        if not recent or not historic:
            continue

        recent_count    = sum(r["count"] for r in recent) / len(recent)
        historic_count  = sum(r["count"] for r in historic) / len(historic)

        if historic_count < 1:
            continue

        surge_ratio = recent_count / historic_count

        if surge_ratio >= min_surge_ratio and recent_count >= min_papers:
            recent_score   = sum(r["avg_score"] for r in recent) / len(recent)
            historic_score = sum(r["avg_score"] for r in historic) / len(historic)
            score_delta    = round(recent_score - historic_score, 3)

            surges.append({
                "field":         field,
                "surge_ratio":   round(surge_ratio, 2),
                "recent_count":  round(recent_count, 1),
                "score_delta":   score_delta,
                "label":         _classify_surge(surge_ratio, score_delta),
            })

    surges.sort(key=lambda x: x["surge_ratio"], reverse=True)
    return surges


def _classify_surge(ratio: float, score_delta: float) -> str:
    if ratio >= 3.0 and score_delta > 0.5:
        return "🔥 Explosive Emergence"
    elif ratio >= 2.0:
        return "📈 Rapid Growth"
    elif ratio >= 1.5:
        return "🌱 Early Emergence"
    else:
        return "📊 Mild Uptick"


def detect_convergence_fields(papers: list[dict]) -> list[dict]:
    """
    Given today's papers, detect which CONVERGENCE_SIGNALS are being triggered.
    A convergence fires if:
      - Papers from 2+ of the signal's fields are present, AND
      - At least 1 keyword matches in any paper's text
    """
    today_domains = set(p.get("domain", "") for p in papers)

    detected = []
    for signal in CONVERGENCE_SIGNALS:
        domains_hit = [f for f in signal["fields"] if f in today_domains]
        if len(domains_hit) < 2:
            continue

        # Check keyword presence across all papers
        all_text = " ".join(
            (p.get("title", "") + " " + p.get("abstract", "")).lower()
            for p in papers
        )
        kw_hits = [kw for kw in signal["keywords"] if kw.lower() in all_text]

        if kw_hits:
            detected.append({
                "name":         signal["name"],
                "domains_hit":  domains_hit,
                "keywords_hit": kw_hits,
                "confidence":   round(len(domains_hit) / len(signal["fields"]), 2),
            })

    detected.sort(key=lambda x: x["confidence"], reverse=True)
    return detected


# ─────────────────────────────────────────────────────────────────────────────
# PUBLIC API
# ─────────────────────────────────────────────────────────────────────────────

def get_emerging_trends(papers: list[dict]) -> list[dict]:
    """
    Main entry point called from main.py.
    Returns a ranked list of emerging trend dicts for use in the email digest.
    Each trend has: name, description, type (convergence | surge), confidence
    """
    trends = []

    # 1. Real-time convergence detection from today's papers
    for c in detect_convergence_fields(papers):
        trends.append({
            "name":        c["name"],
            "description": f"Convergence detected across: {', '.join(c['domains_hit'])}",
            "type":        "convergence",
            "confidence":  c["confidence"],
        })

    # 2. Historical momentum surges from DB
    for s in detect_momentum_surges(days=14, min_surge_ratio=1.5):
        trends.append({
            "name":        s["field"],
            "description": f"{s['label']} — {s['surge_ratio']}× paper volume increase",
            "type":        "surge",
            "confidence":  min(s["surge_ratio"] / 4.0, 1.0),
        })

    # Deduplicate by name (convergence takes priority over surge for same field)
    seen  = set()
    deduped = []
    for t in trends:
        if t["name"] not in seen:
            seen.add(t["name"])
            deduped.append(t)

    return deduped[:8]  # Top 8 trends max


if __name__ == "__main__":
    surges = detect_momentum_surges(days=14)
    print(f"\n📈 Momentum Surges (last 14 days):")
    for s in surges:
        print(f"  {s['label']} — {s['field']} ({s['surge_ratio']}×)")

    print(f"\nNo live paper list available for convergence detection in CLI mode.")
