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
import json

# ── Import all fetchers ───────────────────────────────────────────────────────
from fetch_papers import (
    fetch_arxiv, fetch_pubmed, fetch_openalex, fetch_biorxiv,
    fetch_semantic_scholar, cluster_discoveries, days_ago, safe_get,
    ARXIV_CATEGORIES, PUBMED_QUERIES, OPENALEX_CONCEPTS,
)
from v2_fetchers import (
    fetch_nih_grants, fetch_github_repos, fetch_patents,
    fetch_conferences, fetch_datasets, fetch_startup_funding_rss
)
from fetch_clinical_trials import fetch_recent_oncology_trials
from dashboard_config import PARADIGMS
import hashlib

# Ordered longest/most-specific patterns first so "synthetic biology" beats "biology",
# and medical terms route to "Medicine" instead of defaulting to chunk[0] ("Mathematics").
_PARADIGM_RULES: list[tuple[str, tuple[str, ...]]] = [
    ("Synthetic Biology", ("synthetic biology", "crispr", "gene circuit", "metabolic engineering")),
    ("Artificial Intelligence", ("artificial intelligence", "machine learning", "deep learning", "large language model", "llm", "neural network", "transformer", "generative ai", "foundation model")),
    ("Quantum Computing", ("quantum computing", "qubit", "quantum algorithm", "quantum error", "superconducting quantum")),
    ("Neuroscience", ("neuroscience", "neural circuit", "connectome", "brain", "synap", "alzheimer", "parkinson", "cognitive")),
    ("Materials Science", ("materials science", "metamaterial", "perovskite", "battery", "catalyst", "graphene", "polymer", "nanomaterial")),
    ("Climate Science", ("climate change", "carbon capture", "greenhouse", "decarbonization", "renewable")),
    ("Environmental Science", ("environmental", "ecology", "biodiversity", "pollution", "watershed")),
    ("Earth Science", ("geology", "seismic", "geophys", "oceanograph", "atmospheric")),
    ("Astronomy", ("astronomy", "astrophys", "exoplanet", "galaxy", "cosmolog", "telescope")),
    ("Medicine", ("cancer", "oncology", "tumor", "carcinoma", "fgfr4", "clinical", "therapeutic", "drug discovery", "patient", "disease", "alzheimer", "dementia", "immunotherapy", "kinase", "biomarker", "vaccine", "pharmac", "circadian")),
    ("Biology", ("biology", "genom", "proteom", "protein", "bioinformatics", "cell", "rna", "dna", "microbiome", "molecular dynamics", "enzyme")),
    ("Chemistry", ("chemistry", "chemical", "organic synthesis", "catalysis", "molecule", "ligand")),
    ("Computer Science", ("computer science", "algorithm", "software", "compiler", "distributed system", "cryptography", "cybersecurity", "robotics", "open source")),
    ("Physics", ("physics", "photon", "laser", "condensed matter", "particle", "plasma", "optical")),
    ("Mathematics", ("mathematics", "theorem", "topology", "algebra", "differential equation", "manifold")),
    ("Statistics", ("statistics", "statistical", "bayesian", "regression", "causal inference")),
    ("Engineering", ("engineering", "hardware", "semiconductor", "robotics", "actuator", "aerospace")),
    ("Economics", ("economics", "macroeconomic", "fintech", "market")),
    ("Public Health", ("public health", "epidemiology", "pandemic", "health equity")),
    ("Agriculture", ("agriculture", "crop", "soil", "agritech")),
    ("Education", ("education", "pedagogy", "learning analytics")),
]


def infer_paradigm_domain(item: dict, default_domain: str = "Other") -> str:
    """Infer the closest PARADIGM domain from an item's title and abstract."""
    text = f"{item.get('title', '')} {item.get('abstract', '')}".lower()
    for paradigm, keywords in _PARADIGM_RULES:
        if any(kw in text for kw in keywords):
            return paradigm
    return default_domain if default_domain in PARADIGMS else "Other"


def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))


def assign_domain_from_chunk(item, chunk, fallback: str = "Other"):
    """Assign an accurate scientific domain rather than blindly defaulting to chunk[0]."""
    inferred = infer_paradigm_domain(item, default_domain="")
    if inferred and inferred != "Other":
        return inferred
    text = (item.get("title", "") + " " + item.get("abstract", "")).lower()
    for c in chunk:
        if c.lower() in text:
            return c
    return fallback if fallback in PARADIGMS else "Other"

# ─────────────────────────────────────────────────────────────────────────────
# SOURCE REGISTRY
# Add new sources here. Do NOT touch fetch_all_papers() to add a source.
# ─────────────────────────────────────────────────────────────────────────────

def _fetch_all_arxiv():
    papers = []
    for domain, cats in ARXIV_CATEGORIES.items():
        batch = fetch_arxiv(cats, max_results=int(os.environ.get("PAPERS_PER_SOURCE", "15")))
        for p in batch:
            p["domain"] = domain
            p["source_types"] = ["paper"]
        papers.extend(batch)
        time.sleep(1)
    return papers

def _fetch_all_pubmed():
    papers = []
    for domain, query in PUBMED_QUERIES.items():
        batch = fetch_pubmed(query, max_results=int(os.environ.get("PAPERS_PER_SOURCE", "15")))
        for p in batch:
            p["domain"] = domain
            p["source_types"] = ["paper"]
        papers.extend(batch)
        time.sleep(0.8)
    return papers

def _fetch_all_openalex():
    names = [
        "Computer Science", "Physics", "Mathematics", "Biology", "Medicine",
        "Economics", "Sociology", "Psychology", "Philosophy", "Materials Science", "Engineering",
    ]
    papers = []
    for cid, name in zip(OPENALEX_CONCEPTS, names):
        batch = fetch_openalex(cid, max_results=10)
        for p in batch:
            p["domain"] = name
            p["source_types"] = ["paper"]
        papers.extend(batch)
        time.sleep(0.3)
    return papers

def _fetch_all_biorxiv():
    papers = []
    for cat in ["bioinformatics", "cancer biology", "neuroscience", "systems biology"]:
        batch = fetch_biorxiv(cat, max_results=15, server="biorxiv")
        for p in batch:
            p["source_types"] = ["paper"]
        papers.extend(batch)
        time.sleep(0.4)
    for cat in ["oncology", "health informatics", "infectious diseases"]:
        batch = fetch_biorxiv(cat, max_results=10, server="medrxiv")
        for p in batch:
            p["source_types"] = ["paper"]
        papers.extend(batch)
        time.sleep(0.4)
    return papers

def _fetch_all_semantic_scholar():
    queries = [
        "large language models science",
        "CRISPR gene therapy clinical",
        "drug discovery AI generative",
        "oncology circadian biomarker",
    ]
    papers = []
    for q in queries:
        batch = fetch_semantic_scholar(q, max_results=4)
        for p in batch:
            p["source_types"] = ["paper"]
        papers.extend(batch)
        time.sleep(2.5)
    # Also pull high-citation recent 30-day papers via OpenAlex as a reliable zero-429 citation momentum feed
    since_30 = days_ago(30)
    for cid, name in [("C41008148", "Computer Science"), ("C86803240", "Biology"), ("C71924100", "Medicine")]:
        url = (
            f"https://api.openalex.org/works?"
            f"filter=concepts.id:{cid},from_publication_date:{since_30},type:article|preprint,has_abstract:true"
            f"&sort=cited_by_count:desc&per-page=3&mailto=research@example.com"
        )
        raw = safe_get(url)
        if raw:
            try:
                data = json.loads(raw)
                for w in data.get("results", []):
                    title = (w.get("title") or "").strip()
                    if not title:
                        continue
                    abstract_inv = w.get("abstract_inverted_index")
                    abstract = ""
                    if abstract_inv:
                        word_pos = {pos: word for word, positions in abstract_inv.items() for pos in positions}
                        abstract = " ".join(word_pos[i] for i in sorted(word_pos))[:800]
                    doi = w.get("doi", "")
                    oa_url = w.get("open_access", {}).get("oa_url", "") or w.get("primary_location", {}).get("landing_page_url", "") or (f"https://doi.org/{doi}" if doi else "")
                    papers.append({
                        "source": "OpenAlex (Cited)",
                        "id": w.get("id", ""),
                        "title": title,
                        "abstract": abstract,
                        "authors": [a.get("author", {}).get("display_name", "") for a in w.get("authorships", [])[:4]],
                        "date": w.get("publication_date", ""),
                        "url": oa_url,
                        "pdf_url": w.get("open_access", {}).get("oa_url", ""),
                        "domain": name,
                        "cited_by": w.get("cited_by_count", 0),
                        "source_types": ["paper"],
                    })
            except Exception:
                pass
    return papers

def _fetch_all_nih():
    """Fetch diverse recent NIH grants across domain-specific queries (avoiding cross-chunk overlap)."""
    queries = [
        ("cancer OR oncology OR tumor OR kinase", "Medicine"),
        ("artificial intelligence OR machine learning OR computational biology", "Artificial Intelligence"),
        ("circadian OR neuroscience OR neurodegeneration OR alzheimer", "Neuroscience"),
        ("CRISPR OR synthetic biology OR genomics OR vaccine", "Synthetic Biology"),
    ]
    results = []
    for query, fallback in queries:
        batch = fetch_nih_grants(query, max_results=5)
        for p in batch:
            p["source_types"] = ["grant"]
            p["domain"] = infer_paradigm_domain(p, default_domain=fallback)
        results.extend(batch)
        time.sleep(0.4)
    return results


def _fetch_all_github():
    results = []
    # GitHub Search API caps boolean queries at max 5 AND/OR/NOT operators -> chunk size <= 5
    for chunk in chunker(PARADIGMS, 5):
        query = " OR ".join(f'"{c}"' for c in chunk)
        batch = fetch_github_repos(query, max_results=4)
        for p in batch:
            p["source_types"] = ["repo"]
            p["domain"] = assign_domain_from_chunk(p, chunk, fallback="Computer Science")
        results.extend(batch)
    return results


def _fetch_all_patents():
    """Fetch patents across multiple scientific domains via simple non-timing-out terms."""
    patent_queries = [
        ("cancer", "Medicine"),
        ("protein", "Biology"),
        ("neural", "Neuroscience"),
        ("quantum", "Quantum Computing"),
        ("algorithm", "Artificial Intelligence"),
        ("biosensor", "Engineering"),
    ]
    results = []
    for query, default_domain in patent_queries:
        batch = fetch_patents(query, max_results=3)
        for p in batch:
            p["source_types"] = ["patent"]
            p["domain"] = infer_paradigm_domain(p, default_domain=default_domain)
        results.extend(batch)
        time.sleep(0.5)
    return results


def _fetch_all_conferences():
    """Fetch recent peer-reviewed flagship journals & AI/Bio venues via OpenAlex."""
    venues = [
        ("issn:0028-0836", "Biology"),   # Nature
        ("issn:0036-8075", "Biology"),   # Science
        ("issn:0092-8674", "Biology"),   # Cell
        ("issn:1087-0156", "Biology"),   # Nature Biotechnology
        ("issn:1367-4803", "Biology"),   # Bioinformatics
        ("NeurIPS", "Artificial Intelligence"),
        ("ICML", "Artificial Intelligence"),
    ]
    results = []
    for venue, default_domain in venues:
        batch = fetch_conferences(venue, max_results=4)
        for p in batch:
            p["source_types"] = ["paper"]
            p["domain"] = infer_paradigm_domain(p, default_domain=default_domain)
        results.extend(batch)
        time.sleep(0.3)
    return results


def _fetch_all_datasets():
    """Fetch recent open scientific datasets & technical resources via Zenodo + HuggingFace."""
    queries = [
        ("oncology", "Medicine"),
        ("protein", "Biology"),
        ("machine learning", "Artificial Intelligence"),
        ("quantum", "Physics"),
        ("climate", "Climate Science"),
    ]
    results = []
    for q, default_domain in queries:
        batch = fetch_datasets(q, max_results=4)
        for p in batch:
            p["source_types"] = ["dataset"]
            p["domain"] = infer_paradigm_domain(p, default_domain=default_domain)
        results.extend(batch)
        time.sleep(0.3)
    return results


def _fetch_all_funding():
    results = []
    for chunk in chunker(PARADIGMS, 8):
        query = " OR ".join(f'"{c}"' for c in chunk)
        batch = fetch_startup_funding_rss(query, max_results=4)
        for p in batch:
            p["source_types"] = ["funding"]
            p["domain"] = assign_domain_from_chunk(p, chunk, fallback="Business & Management")
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
        "description": "Peer-reviewed flagship journals and AI/Bio proceedings via OpenAlex",
    },
    {
        "name":        "Scientific Datasets",
        "type":        "dataset",
        "enabled":     True,
        "fetcher":     _fetch_all_datasets,
        "description": "Open scientific datasets from Zenodo and HuggingFace",
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
    max_total = int(os.environ.get("MAX_PAPERS_TOTAL", "500"))

    enabled = [s for s in SOURCE_REGISTRY if s["enabled"]]
    print(f"\n📡 Running {len(enabled)} enabled source(s) concurrently...\n")

    import concurrent.futures
    try:
        import langdetect
    except ImportError:
        langdetect = None
    
    def is_english(text):
        if not langdetect or not text or len(text.strip()) < 20: return True
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
    raw_scanned_count = len(all_items)

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

    # Fair round-robin cap across sources if pool exceeds max_total,
    # preventing fast APIs from starving slower ones (PubMed, Patents, ClinicalTrials).
    if len(all_items) > max_total:
        from collections import defaultdict
        by_src = defaultdict(list)
        for item in all_items:
            by_src[item.get("source", "Other")].append(item)
        balanced = []
        buckets = list(by_src.values())
        idx = 0
        while len(balanced) < max_total and any(idx < len(b) for b in buckets):
            for b in buckets:
                if idx < len(b) and len(balanced) < max_total:
                    balanced.append(b[idx])
            idx += 1
        all_items = balanced

    total_fetched = len(all_items)
    print(f"\n✅ Scanned {raw_scanned_count} raw items → {total_fetched} unique discoveries after deduplication & clustering")
    fetch_all_intelligence.last_raw_count = raw_scanned_count
    return all_items
