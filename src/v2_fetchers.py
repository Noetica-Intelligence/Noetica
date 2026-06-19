import urllib.request
import urllib.parse
import json
import time
import ssl
from typing import List, Dict, Any
from datetime import datetime

ssl._create_default_https_context = ssl._create_unverified_context

# ─────────────────────────────────────────────
# NIH REPORTER API (GRANT TRACKING)
# ─────────────────────────────────────────────

def fetch_nih_grants(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """Fetch recent grants from NIH RePORTER API."""
    url = "https://api.reporter.nih.gov/v2/projects/search"
    payload = {
        "criteria": {
            "advanced_text_search": {
                "operator": "and",
                "search_text": query
            }
        },
        "limit": max_results,
        "sort_field": "project_start_date",
        "sort_order": "desc"
    }
    
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("accept", "application/json")
    
    results = []
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            for item in data.get("results", []):
                title = item.get("project_title", "")
                abstract = item.get("abstract_text", "")
                org = item.get("organization", {}).get("org_name", "Unknown Org")
                pi = item.get("principal_investigators", [{"pi_name": "Unknown"}])[0].get("pi_name")
                cost = item.get("award_amount", 0)
                
                results.append({
                    "id": f"nih_{item.get('appl_id')}",
                    "title": f"[GRANT] {title}",
                    "abstract": abstract if abstract else f"Grant awarded to {org} for {cost}",
                    "authors": [pi],
                    "source": "NIH RePORTER",
                    "domain": "Biomedical Funding",
                    "date": item.get("project_start_date", datetime.today().isoformat()),
                    "url": f"https://reporter.nih.gov/project-details/{item.get('appl_id')}",
                    "funding_amount": cost
                })
    except Exception as e:
        print(f"⚠️ NIH Fetch Error for '{query}': {e}")
        
    return results

# ─────────────────────────────────────────────
# GITHUB API (OPEN SOURCE INTELLIGENCE)
# ─────────────────────────────────────────────

def fetch_github_repos(topic: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """Fetch trending repositories from GitHub API."""
    # Search for repos created/updated recently sorted by stars
    safe_topic = urllib.parse.quote(topic)
    url = f"https://api.github.com/search/repositories?q={safe_topic}+stars:>50&sort=updated&order=desc&per_page={max_results}"
    
    req = urllib.request.Request(url, headers={"User-Agent": "Scientific-Intelligence-V2"})
    
    results = []
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            for item in data.get("items", []):
                results.append({
                    "id": f"gh_{item.get('id')}",
                    "title": f"[REPO] {item.get('full_name')}",
                    "abstract": item.get("description", "No description provided."),
                    "authors": [item.get("owner", {}).get("login", "Unknown")],
                    "source": "GitHub",
                    "domain": "Open Source Software",
                    "date": item.get("updated_at", datetime.today().isoformat()),
                    "url": item.get("html_url", ""),
                    "stars": item.get("stargazers_count", 0)
                })
    except Exception as e:
        print(f"⚠️ GitHub Fetch Error for '{topic}': {e}")
        
    return results

# ─────────────────────────────────────────────
# MOCK PATENT API (USPTO/WIPO)
# ─────────────────────────────────────────────
# Real patent APIs (e.g. PatentsView) are heavily rate-limited and complex.
# For V2 MVP, we simulate a patent fetcher structure.

def fetch_patents(query: str, max_results: int = 3) -> List[Dict[str, Any]]:
    """Simulated fetch for recent patents."""
    results = [
        {
            "id": f"pat_mock_1",
            "title": f"[PATENT] Novel methods for {query}",
            "abstract": f"A patent describing commercialization techniques and methods related to {query}.",
            "authors": ["Inventor A", "Inventor B"],
            "source": "USPTO",
            "domain": "Technology Patent",
            "date": datetime.today().isoformat(),
            "url": "https://patents.google.com/",
        }
    ]
    return results

# ─────────────────────────────────────────────
# ORCHESTRATOR FOR V2 FETCHERS
# ─────────────────────────────────────────────

def fetch_v2_intelligence() -> List[Dict[str, Any]]:
    """Fetches Grants, Open Source Repos, and Patents."""
    all_intel = []
    
    print("\n💰 Fetching NIH Grants...")
    for q in ["crispr", "machine learning", "quantum"]:
        all_intel.extend(fetch_nih_grants(q, 2))
        time.sleep(1)
        
    print("\n💻 Fetching GitHub Open Source...")
    for q in ["deep-learning", "bioinformatics", "quantum-computing"]:
        all_intel.extend(fetch_github_repos(q, 2))
        time.sleep(1)
        
    print("\n📜 Fetching Patents...")
    for q in ["LLM architectures", "gene editing"]:
        all_intel.extend(fetch_patents(q, 1))
        
    return all_intel

if __name__ == "__main__":
    results = fetch_v2_intelligence()
    print(f"\n✅ Fetched {len(results)} non-paper intelligence nodes.")
    for r in results:
        print(f" - {r['title']}")
