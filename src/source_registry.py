"""
Scientific Intelligence Engine — Source Registry (Plug-in Architecture)
New sources are added here by adding an entry to SOURCE_REGISTRY.
Core fetch logic never needs to change.

Each source entry is a dict:
    {
        "name":        str,        # display name
        "type":        str,        # "paper" | "patent" | "grant" | "repo" | "trial"
        "enabled":     bool,       # toggle without deleting
        "fetcher":     callable,   # function() -> list[dict]
        "rate_limit":  float,      # seconds to sleep after fetch
        "description": str,
    }
"""

import time
import os

# ── Import all fetchers ───────────────────────────────────────────────────────
from fetch_papers import (
    fetch_arxiv, fetch_pubmed, fetch_openalex, fetch_biorxiv,
    fetch_semantic_scholar, cluster_discoveries,
    ARXIV_CATEGORIES, PUBMED_QUERIES, OPENALEX_CONCEPTS,
)
from v2_fetchers import (
    fetch_nih_grants, fetch_github_repos, fetch_patents,
    fetch_conferences, fetch_startup_funding_rss
)
from fetch_clinical_trials import fetch_recent_oncology_trials
from dashboard_config import PARADIGMS
import hashlib

def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))

def assign_domain_from_chunk(item, chunk):
    text = (item.get("title", "") + " " + item.get("abstract", "")).lower()
    for c in chunk:
        if c.lower() in text:
            return c
    return chunk[0]

# ─────────────────────────────────────────────────────────────────────────────
# SOURCE REGISTRY
# Add new sources here. Do NOT touch fetch_all_papers() to add a source.
# ─────────────────────────────────────────────────────────────────────────────

def _fetch_all_arxiv():
    papers = []
    for domain, cats in ARXIV_CATEGORIES.items():
        batch = fetch_arxiv(cats, max_results=int(os.environ.get("PAPERS_PER_SOURCE", "5")))
        for p in batch:
            p["domain"] = domain
            p["source_types"] = ["paper"]
        papers.extend(batch)
        time.sleep(1)
    return papers

def _fetch_all_pubmed():
    papers = []
    for domain, query in PUBMED_QUERIES.items():
        batch = fetch_pubmed(query, max_results=int(os.environ.get("PAPERS_PER_SOURCE", "5")))
        for p in batch:
            p["domain"] = domain
            p["source_types"] = ["paper"]
        papers.extend(batch)
        time.sleep(0.5)
    return papers

def _fetch_all_openalex():
    names = [
        "Computer Science", "Physics", "Mathematics", "Biology", "Medicine",
        "Economics", "Sociology", "Psychology", "Philosophy", "Materials Science", "Engineering",
    ]
    papers = []
    for cid, name in zip(OPENALEX_CONCEPTS, names):
        batch = fetch_openalex(cid, max_results=3)
        for p in batch:
            p["domain"] = name
            p["source_types"] = ["paper"]
        papers.extend(batch)
        time.sleep(0.5)
    return papers

def _fetch_all_biorxiv():
    papers = []
    for cat in ["bioinformatics", "cancer biology", "neuroscience", "systems biology"]:
        batch = fetch_biorxiv(cat, max_results=4)
        for p in batch:
            p["source_types"] = ["paper"]
        papers.extend(batch)
        time.sleep(0.5)
    return papers

def _fetch_all_semantic_scholar():
    queries = [
        "large language models science",
        "quantum computing algorithms",
        "CRISPR gene therapy clinical",
        "drug discovery AI generative",
        "climate change machine learning",
        "philosophy of mind consciousness",
        "behavioral economics decision making",
    ]
    papers = []
    for q in queries:
        batch = fetch_semantic_scholar(q, max_results=3)
        for p in batch:
            p["source_types"] = ["paper"]
        papers.extend(batch)
        time.sleep(1.5)   # Semantic Scholar rate-limit friendly
    return papers

def _fetch_all_nih():
    results = []
    for chunk in chunker(PARADIGMS, 4):
        query = " OR ".join(f'"{c}"' for c in chunk)
        batch = fetch_nih_grants(query, max_results=3)
        for p in batch:
            p["source_types"] = ["grant"]
            p["domain"] = assign_domain_from_chunk(p, chunk)
        results.extend(batch)
    return results

def _fetch_all_github():
    results = []
    for chunk in chunker(PARADIGMS, 4):
        query = " OR ".join(f'"{c}"' for c in chunk)
        batch = fetch_github_repos(query, max_results=3)
        for p in batch:
            p["source_types"] = ["repo"]
            p["domain"] = assign_domain_from_chunk(p, chunk)
        results.extend(batch)
    return results

def _fetch_all_patents():
    results = []
    for chunk in chunker(PARADIGMS, 4):
        query = " OR ".join(f'"{c}"' for c in chunk)
        batch = fetch_patents(query, max_results=2)
        for p in batch:
            p["source_types"] = ["patent"]
            p["domain"] = assign_domain_from_chunk(p, chunk)
        results.extend(batch)
    return results

def _fetch_all_conferences():
    results = []
    for venue in ["NeurIPS", "ICML", "Nature", "Cell", "Science", "CVPR"]:
        batch = fetch_conferences(venue, max_results=2)
        for p in batch:
            p["source_types"] = ["paper"]
        results.extend(batch)
        time.sleep(1)
    return results

def _fetch_all_funding():
    results = []
    for chunk in chunker(PARADIGMS, 4):
        query = " OR ".join(f'"{c}"' for c in chunk)
        batch = fetch_startup_funding_rss(query, max_results=2)
        for p in batch:
            p["source_types"] = ["funding"]
            p["domain"] = assign_domain_from_chunk(p, chunk)
        results.extend(batch)
    return results

def _fetch_clinical_trials():
    trials = fetch_recent_oncology_trials(days_back=7)
    for t in trials:
        t["source_types"] = ["trial"]
    return trials


# ─────────────────────────────────────────────────────────────────────────────
# REGISTRY — Edit this to enable/disable/add sources
# ─────────────────────────────────────────────────────────────────────────────

SOURCE_REGISTRY = [
    {
        "name":        "arXiv",
        "type":        "paper",
        "enabled":     True,
        "fetcher":     _fetch_all_arxiv,
        "rate_limit":  1.0,
        "description": "Preprint server for physics, math, and CS",
    },
    {
        "name":        "PubMed",
        "type":        "paper",
        "enabled":     True,
        "fetcher":     _fetch_all_pubmed,
        "description": "Biomedical literature via NCBI E-utilities",
    },
    {
        "name":        "OpenAlex",
        "type":        "paper",
        "enabled":     True,
        "fetcher":     _fetch_all_openalex,
        "description": "Open scholarly graph — interdisciplinary coverage",
    },
    {
        "name":        "bioRxiv",
        "type":        "paper",
        "enabled":     True,
        "fetcher":     _fetch_all_biorxiv,
        "description": "Life science preprints",
    },
    {
        "name":        "Semantic Scholar",
        "type":        "paper",
        "enabled":     True,
        "fetcher":     _fetch_all_semantic_scholar,
        "description": "AI-powered paper search with citation data",
    },
    {
        "name":        "NIH RePORTER",
        "type":        "grant",
        "enabled":     True,
        "fetcher":     _fetch_all_nih,
        "description": "NIH grant awards — signals future research directions",
    },
    {
        "name":        "GitHub",
        "type":        "repo",
        "enabled":     True,
        "fetcher":     _fetch_all_github,
        "description": "Open-source repositories — builder activity signal",
    },
    {
        "name":        "Patents",
        "type":        "patent",
        "enabled":     True,
        "fetcher":     _fetch_all_patents,
        "description": "Patent activity — commercialization intent signal",
    },
    {
        "name":        "ClinicalTrials.gov",
        "type":        "trial",
        "enabled":     True,
        "fetcher":     _fetch_clinical_trials,
        "description": "Oncology clinical trials — real-world translation signal",
    },
    {
        "name":        "Conferences",
        "type":        "paper",
        "enabled":     True,
        "fetcher":     _fetch_all_conferences,
        "description": "Peer-reviewed AI/Bio conference proceedings",
    },
    {
        "name":        "Venture Capital Feeds",
        "type":        "funding",
        "enabled":     True,
        "fetcher":     _fetch_all_funding,
        "description": "Startup funding rounds from unified RSS streams",
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# MAIN FETCH ORCHESTRATOR (replaces fetch_all_papers)
# ─────────────────────────────────────────────────────────────────────────────

def fetch_all_intelligence() -> list[dict]:
    """
    Fetch from all enabled sources in the registry.
    Returns a deduplicated, clustered list of discovery dicts.
    """
    all_items: list[dict] = []
    max_total = int(os.environ.get("MAX_PAPERS_TOTAL", "60"))

    enabled = [s for s in SOURCE_REGISTRY if s["enabled"]]
    print(f"\n📡 Running {len(enabled)} enabled source(s) concurrently...\n")

    import concurrent.futures
    import langdetect
    
    def is_english(text):
        if not text or len(text.strip()) < 20: return True
        try:
            return langdetect.detect(text) == 'en'
        except:
            return True

    def fetch_source(source):
        print(f"  [{source['type'].upper()}] {source['name']} — {source['description']}")
        try:
            items = source["fetcher"]()
            valid_items = []
            for item in items:
                # Discard non-English discoveries
                if not is_english(item.get("abstract", "")):
                    continue
                if not item.get("source"):
                    item["source"] = source["name"]
                valid_items.append(item)
            print(f"    → {len(valid_items)} items fetched from {source['name']}")
            return valid_items
        except Exception as e:
            print(f"    ⚠️  {source['name']} failed: {e}")
            return []

    # Blast all APIs simultaneously for 80% speed increase
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(enabled)) as executor:
        futures = [executor.submit(fetch_source, s) for s in enabled]
        for future in concurrent.futures.as_completed(futures):
            all_items.extend(future.result())

    # Filter: must have title
    all_items = [i for i in all_items if i.get("title")]

    # SHA-256 Deduplication Failsafe (Cross-Paradigm)
    seen_hashes = set()
    deduped_items = []
    for item in all_items:
        text = (item.get("title", "") + item.get("abstract", "")).lower().strip()
        h = hashlib.sha256(text.encode('utf-8', 'replace')).hexdigest()
        if h not in seen_hashes:
            seen_hashes.add(h)
            deduped_items.append(item)
    all_items = deduped_items

    # Cluster duplicates (by title similarity)
    all_items = cluster_discoveries(all_items)

    print(f"\n✅ Total unique discoveries after deduplication & clustering: {len(all_items)}")
    return all_items
