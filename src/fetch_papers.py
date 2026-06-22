"""
Scientific Intelligence Engine — Paper Fetcher
Fetches top papers from arXiv, PubMed, OpenAlex, and bioRxiv
across all configured research domains.
"""

import os
import json
import time
import datetime
import urllib.request
import urllib.parse
import urllib.error
import xml.etree.ElementTree as ET
from pathlib import Path

# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────

# Map of domains → arXiv category codes
ARXIV_CATEGORIES = {
    "Theoretical Physics":   ["hep-th", "gr-qc", "quant-ph"],
    "Experimental Physics":  ["hep-ex", "cond-mat", "physics.optics"],
    "Astrophysics":          ["astro-ph.GA", "astro-ph.CO", "astro-ph.HE"],
    "Pure Mathematics":      ["math.NT", "math.AG", "math.AT"],
    "Applied Mathematics":   ["math.OC", "math.DS", "cs.NA"],
    "Statistics":            ["stat.ML", "stat.TH", "stat.ME"],
    "AI & Machine Learning": ["cs.LG", "cs.AI", "cs.CL"],
    "Bioinformatics":        ["q-bio.GN", "q-bio.BM", "q-bio.QM"],
    "Quantum Computing":     ["quant-ph", "cs.ET"],
    "Cryptography":          ["cs.CR"],
    "Systems CS":            ["cs.DC", "cs.OS"],
    "Robotics":              ["cs.RO"],
    "Materials Science":     ["cond-mat.mtrl-sci"],
}

# PubMed search queries per domain
PUBMED_QUERIES = {
    "Oncology":              "hepatocellular carcinoma FGFR4 drug discovery[Title/Abstract]",
    "Circadian Biology":     "circadian rhythms chronotherapy drug timing[Title/Abstract]",
    "AI in Medicine":        "artificial intelligence drug discovery precision medicine[Title/Abstract]",
    "GNNs for Biology":      "graph neural network drug discovery bioinformatics[Title/Abstract]",
    "Molecular Dynamics":    "molecular dynamics simulation drug target[Title/Abstract]",
    "Structural Biology":    "AlphaFold protein structure prediction[Title/Abstract]",
    "Immunology":            "cancer immunotherapy checkpoint inhibitor[Title/Abstract]",
    "Neuroscience":          "computational neuroscience brain connectome[Title/Abstract]",
    "Systems Biology":       "systems biology network analysis disease[Title/Abstract]",
    "Synthetic Biology":     "synthetic biology CRISPR gene editing[Title/Abstract]",
}

# OpenAlex topics (concept IDs — broad and interdisciplinary)
OPENALEX_CONCEPTS = [
    "C41008148",   # Computer Science
    "C121332964",  # Physics
    "C33923547",   # Mathematics
    "C86803240",   # Biology
    "C71924100",   # Medicine
    "C162324750",  # Economics
    "C144024400",  # Sociology
    "C15744967",   # Psychology
    "C138885662",  # Philosophy
    "C192562407",  # Materials Science
    "C127413603",  # Engineering
]

PAPERS_PER_SOURCE = int(os.environ.get("PAPERS_PER_SOURCE", "5"))
MAX_PAPERS_TOTAL  = int(os.environ.get("MAX_PAPERS_TOTAL", "60"))


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def safe_get(url: str, timeout: int = 20) -> bytes | None:
    """HTTP GET with retry logic."""
    headers = {"User-Agent": "ScientificIntelligenceBot/1.0 (research digest; contact: research@example.com)"}
    req = urllib.request.Request(url, headers=headers)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except Exception as e:
            print(f"  [WARN] Attempt {attempt+1} failed for {url[:80]}: {e}")
            time.sleep(2 ** attempt)
    return None


def today_iso() -> str:
    return datetime.date.today().isoformat()


def days_ago(n: int) -> str:
    return (datetime.date.today() - datetime.timedelta(days=n)).isoformat()


# ─────────────────────────────────────────────
# ARXIV FETCHER
# ─────────────────────────────────────────────

def fetch_arxiv(categories: list[str], max_results: int = 5) -> list[dict]:
    """Fetch latest papers from arXiv for given category codes."""
    cat_query = "+OR+".join(f"cat:{c}" for c in categories)
    url = (
        f"http://export.arxiv.org/api/query?"
        f"search_query={cat_query}"
        f"&sortBy=submittedDate&sortOrder=descending"
        f"&max_results={max_results}"
    )
    raw = safe_get(url)
    if not raw:
        return []

    papers = []
    try:
        root = ET.fromstring(raw)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        for entry in root.findall("atom:entry", ns):
            title   = (entry.findtext("atom:title",   "", ns) or "").strip().replace("\n", " ")
            summary = (entry.findtext("atom:summary", "", ns) or "").strip().replace("\n", " ")
            link_el = entry.find("atom:link[@rel='alternate']", ns)
            link    = link_el.attrib.get("href", "") if link_el is not None else ""
            authors = [a.findtext("atom:name", "", ns) for a in entry.findall("atom:author", ns)]
            pub_date= (entry.findtext("atom:published", "", ns) or "")[:10]
            arxiv_id= link.split("/abs/")[-1] if "/abs/" in link else ""
            papers.append({
                "source":   "arXiv",
                "id":       arxiv_id,
                "title":    title,
                "abstract": summary[:800],
                "authors":  authors[:4],
                "date":     pub_date,
                "url":      link,
                "pdf_url":  link.replace("/abs/", "/pdf/") + ".pdf" if arxiv_id else "",
                "domain":   categories[0],
            })
    except ET.ParseError as e:
        print(f"  [ERROR] arXiv XML parse error: {e}")
    return papers


# ─────────────────────────────────────────────
# PUBMED FETCHER
# ─────────────────────────────────────────────

def fetch_pubmed(query: str, max_results: int = 5) -> list[dict]:
    """Fetch recent papers from PubMed using E-utilities."""
    base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    since = days_ago(3)

    # Step 1: esearch
    search_url = (
        f"{base}/esearch.fcgi?db=pubmed&term={urllib.parse.quote(query)}"
        f"&retmax={max_results}&sort=relevance&retmode=json"
        f"&mindate={since}&maxdate={today_iso()}&datetype=pdat"
    )
    raw = safe_get(search_url)
    if not raw:
        return []
    try:
        ids = json.loads(raw)["esearchresult"]["idlist"]
    except Exception:
        return []
    if not ids:
        return []

    # Step 2: efetch
    fetch_url = f"{base}/efetch.fcgi?db=pubmed&id={','.join(ids)}&retmode=xml"
    raw2 = safe_get(fetch_url)
    if not raw2:
        return []

    papers = []
    try:
        root = ET.fromstring(raw2)
        for article in root.findall(".//PubmedArticle"):
            title = " ".join(
                t.text or "" for t in article.findall(".//ArticleTitle")
            ).strip()
            abstract_parts = article.findall(".//AbstractText")
            abstract = " ".join(
                (a.text or "") for a in abstract_parts
            ).strip()[:800]
            pmid_el  = article.find(".//PMID")
            pmid     = pmid_el.text if pmid_el is not None else ""
            pub_year = article.findtext(".//PubDate/Year", "")
            pub_mon  = article.findtext(".//PubDate/Month", "01")
            pub_day  = article.findtext(".//PubDate/Day", "01")
            pub_date = f"{pub_year}-{pub_mon[:3]}-{pub_day}" if pub_year else ""
            authors  = [
                f"{a.findtext('LastName', '')} {a.findtext('Initials', '')}".strip()
                for a in article.findall(".//Author")[:4]
            ]
            doi_el   = article.find(".//ArticleId[@IdType='doi']")
            doi      = doi_el.text if doi_el is not None else ""
            papers.append({
                "source":   "PubMed",
                "id":       f"pmid:{pmid}",
                "title":    title,
                "abstract": abstract,
                "authors":  authors,
                "date":     pub_date,
                "url":      f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                "pdf_url":  f"https://doi.org/{doi}" if doi else "",
                "domain":   query.split("[")[0][:40],
            })
    except ET.ParseError as e:
        print(f"  [ERROR] PubMed XML parse error: {e}")
    return papers


# ─────────────────────────────────────────────
# OPENALEX FETCHER
# ─────────────────────────────────────────────

def fetch_openalex(concept_id: str, max_results: int = 3) -> list[dict]:
    """Fetch recent highly-cited works from OpenAlex for a concept."""
    since = days_ago(7)
    url = (
        f"https://api.openalex.org/works?"
        f"filter=concepts.id:{concept_id},from_publication_date:{since},is_oa:true"
        f"&sort=cited_by_count:desc"
        f"&per-page={max_results}"
        f"&mailto=research@example.com"
    )
    raw = safe_get(url)
    if not raw:
        return []
    papers = []
    try:
        data = json.loads(raw)
        for w in data.get("results", []):
            title    = w.get("title", "").strip()
            abstract_inv = w.get("abstract_inverted_index")
            abstract = ""
            if abstract_inv:
                word_pos = {pos: word for word, positions in abstract_inv.items() for pos in positions}
                abstract = " ".join(word_pos[i] for i in sorted(word_pos))[:800]
            authors  = [
                a.get("author", {}).get("display_name", "")
                for a in w.get("authorships", [])[:4]
            ]
            date     = w.get("publication_date", "")
            doi      = w.get("doi", "")
            oa_url   = w.get("open_access", {}).get("oa_url", "") or w.get("primary_location", {}).get("landing_page_url", "") or (f"https://doi.org/{doi}" if doi else "")
            cited    = w.get("cited_by_count", 0)
            papers.append({
                "source":   "OpenAlex",
                "id":       w.get("id", ""),
                "title":    title,
                "abstract": abstract,
                "authors":  authors,
                "date":     date,
                "url":      oa_url,
                "pdf_url":  w.get("open_access", {}).get("oa_url", ""),
                "domain":   concept_id,
                "cited_by": cited,
            })
    except json.JSONDecodeError as e:
        print(f"  [ERROR] OpenAlex JSON error: {e}")
    return papers


# ─────────────────────────────────────────────
# BIORXIV FETCHER
# ─────────────────────────────────────────────

def fetch_biorxiv(category: str = "bioinformatics", max_results: int = 5) -> list[dict]:
    """Fetch latest preprints from bioRxiv."""
    since = days_ago(7)
    today = today_iso()
    url = f"https://api.biorxiv.org/details/biorxiv/{since}/{today}/0/json"
    raw = safe_get(url)
    if not raw:
        return []
    papers = []
    try:
        data = json.loads(raw)
        collection = data.get("collection", [])
        filtered = [p for p in collection if category.lower() in (p.get("category") or "").lower()]
        for p in filtered[:max_results]:
            doi = p.get("doi", "")
            papers.append({
                "source":   "bioRxiv",
                "id":       f"biorxiv:{doi}",
                "title":    p.get("title", "").strip(),
                "abstract": (p.get("abstract") or "")[:800],
                "authors":  p.get("authors", "").split(";")[:4],
                "date":     p.get("date", ""),
                "url":      f"https://www.biorxiv.org/content/{doi}",
                "pdf_url":  f"https://www.biorxiv.org/content/{doi}.full.pdf",
                "domain":   category,
            })
    except json.JSONDecodeError as e:
        print(f"  [ERROR] bioRxiv JSON error: {e}")
    return papers


# ─────────────────────────────────────────────
# SEMANTIC SCHOLAR FETCHER (trending papers)
# ─────────────────────────────────────────────

def fetch_semantic_scholar(query: str, max_results: int = 5) -> list[dict]:
    """Fetch recent papers from Semantic Scholar."""
    since = days_ago(7)
    url = (
        f"https://api.semanticscholar.org/graph/v1/paper/search?"
        f"query={urllib.parse.quote(query)}"
        f"&fields=title,abstract,authors,year,externalIds,openAccessPdf,citationCount,publicationDate"
        f"&limit={max_results}"
        f"&publicationDateOrYear={since}:"
    )
    raw = safe_get(url)
    if not raw:
        return []
    papers = []
    try:
        data = json.loads(raw)
        for p in data.get("data", []):
            doi     = p.get("externalIds", {}).get("DOI", "")
            oa_pdf  = (p.get("openAccessPdf") or {}).get("url", "")
            authors = [a.get("name", "") for a in p.get("authors", [])[:4]]
            papers.append({
                "source":   "SemanticScholar",
                "id":       p.get("paperId", ""),
                "title":    (p.get("title") or "").strip(),
                "abstract": (p.get("abstract") or "")[:800],
                "authors":  authors,
                "date":     p.get("publicationDate") or str(p.get("year", "")),
                "url":      f"https://www.semanticscholar.org/paper/{p.get('paperId', '')}",
                "pdf_url":  oa_pdf or (f"https://doi.org/{doi}" if doi else ""),
                "domain":   query,
                "cited_by": p.get("citationCount", 0),
            })
    except json.JSONDecodeError as e:
        print(f"  [ERROR] SemanticScholar JSON error: {e}")
    return papers


# ─────────────────────────────────────────────
# DISCOVERY CLUSTERING ENGINE
# ─────────────────────────────────────────────

def jaccard_similarity(text1: str, text2: str) -> float:
    """Compute token Jaccard similarity between two strings."""
    if not text1 or not text2:
        return 0.0
    
    def tokenize(t):
        import re
        t = t.lower()
        t = re.sub(r'[^a-z0-9\s]', '', t)
        tokens = set(t.split())
        # Remove common stopwords to improve signal
        stopwords = {"the", "a", "an", "and", "or", "but", "in", "on", "with", "to", "for", "of", "is", "are", "was", "were", "by", "this", "that"}
        return tokens - stopwords
        
    set1 = tokenize(text1)
    set2 = tokenize(text2)
    
    if not set1 and not set2:
        return 1.0
    if not set1 or not set2:
        return 0.0
        
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return float(intersection) / float(union)

def cluster_discoveries(papers: list[dict]) -> list[dict]:
    """
    Cluster duplicate papers from multiple sources into a single Discovery entity.
    Uses both exact title matching and abstract Jaccard similarity.
    """
    clusters = []
    
    for p in papers:
        norm_title = "".join(c.lower() for c in p["title"] if c.isalnum())[:60]
        if not norm_title:
            continue
            
        matched_cluster = None
        
        for cluster in clusters:
            # 1. Exact title match
            c_norm_title = "".join(c.lower() for c in cluster["title"] if c.isalnum())[:60]
            if norm_title == c_norm_title:
                matched_cluster = cluster
                break
                
            # 2. Abstract Jaccard similarity
            sim = jaccard_similarity(p.get("abstract", ""), cluster.get("abstract", ""))
            if sim > 0.75: # 75% token overlap is very high
                matched_cluster = cluster
                break
                
        if matched_cluster:
            # Aggregate into the Discovery object
            source_entry = {
                "type": p.get("source_types", ["paper"])[0],
                "name": p.get("source", "Unknown"),
                "url": p.get("url", ""),
                "id": p.get("id", "")
            }
            if "sources" not in matched_cluster:
                # Initialize the first-class sources list
                matched_cluster["sources"] = [{
                    "type": matched_cluster.get("source_types", ["paper"])[0],
                    "name": matched_cluster.get("source", "Unknown"),
                    "url": matched_cluster.get("url", ""),
                    "id": matched_cluster.get("id", "")
                }]
            matched_cluster["sources"].append(source_entry)
            
            # Aggregate authors
            new_authors = [a for a in p.get("authors", []) if a not in matched_cluster.get("authors", [])]
            matched_cluster["authors"].extend(new_authors)
            
            # Prefer peer-reviewed metadata over preprints
            if matched_cluster.get("source") == "arXiv" and p.get("source") != "arXiv":
                matched_cluster["source"] = p.get("source")
                matched_cluster["id"] = p.get("id")
                # Update title to the peer-reviewed version if different
                if len(p["title"]) > 10:
                    matched_cluster["title"] = p["title"]
        else:
            # Initialize as a new Discovery
            p["sources"] = [{
                "type": p.get("source_types", ["paper"])[0],
                "name": p.get("source", "Unknown"),
                "url": p.get("url", ""),
                "id": p.get("id", "")
            }]
            clusters.append(p)
            
    return clusters


# ─────────────────────────────────────────────
# MAIN FETCH ORCHESTRATOR
# ─────────────────────────────────────────────

def fetch_all_papers() -> list[dict]:
    all_papers: list[dict] = []

    print("\n📡 Fetching from arXiv...")
    for domain, cats in ARXIV_CATEGORIES.items():
        print(f"  → {domain}")
        papers = fetch_arxiv(cats, max_results=PAPERS_PER_SOURCE)
        for p in papers:
            p["domain"] = domain
        all_papers.extend(papers)
        time.sleep(1)  # respect rate limits

    print("\n📡 Fetching from PubMed...")
    for domain, query in PUBMED_QUERIES.items():
        print(f"  → {domain}")
        papers = fetch_pubmed(query, max_results=PAPERS_PER_SOURCE)
        for p in papers:
            p["domain"] = domain
        all_papers.extend(papers)
        time.sleep(0.5)

    print("\n📡 Fetching from OpenAlex...")
    openalex_concept_names = [
        "Computer Science", "Physics", "Mathematics", "Biology",
        "Medicine", "Economics", "Sociology", "Psychology",
        "Philosophy", "Materials Science", "Engineering",
    ]
    for concept_id, name in zip(OPENALEX_CONCEPTS, openalex_concept_names):
        print(f"  → {name}")
        papers = fetch_openalex(concept_id, max_results=3)
        for p in papers:
            p["domain"] = name
        all_papers.extend(papers)
        time.sleep(0.5)

    print("\n📡 Fetching from bioRxiv...")
    for cat in ["bioinformatics", "cancer biology", "neuroscience", "systems biology"]:
        print(f"  → {cat}")
        papers = fetch_biorxiv(cat, max_results=4)
        all_papers.extend(papers)
        time.sleep(0.5)

    print("\n📡 Fetching from Semantic Scholar...")
    ss_queries = [
        "large language models science",
        "quantum computing algorithms",
        "CRISPR gene therapy clinical",
        "drug discovery AI generative",
        "climate change machine learning",
        "philosophy of mind consciousness",
        "behavioral economics decision making",
    ]
    for q in ss_queries:
        print(f"  → {q}")
        papers = fetch_semantic_scholar(q, max_results=3)
        all_papers.extend(papers)
        time.sleep(0.5)

    # Filter out papers with no title or abstract
    all_papers = [p for p in all_papers if p.get("title") and p.get("abstract")]

    # Discovery Clustering Engine
    all_papers = cluster_discoveries(all_papers)

    print(f"\n✅ Total unique discoveries clustered: {len(all_papers)}")
    return all_papers[:MAX_PAPERS_TOTAL]


if __name__ == "__main__":
    papers = fetch_all_papers()
    out_path = Path("data") / f"papers_{today_iso()}.json"
    out_path.parent.mkdir(exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(papers, f, indent=2, ensure_ascii=False)
    print(f"💾 Saved {len(papers)} papers → {out_path}")
