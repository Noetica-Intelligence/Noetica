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
# EUROPE PMC API (PATENT INTELLIGENCE)
# ─────────────────────────────────────────────

def fetch_patents(query: str, max_results: int = 3) -> List[Dict[str, Any]]:
    """Fetch real patents via Europe PMC REST API."""
    safe_query = urllib.parse.quote(query)
    url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=SRC:PAT%20AND%20{safe_query}&format=json&resultType=core"
    
    req = urllib.request.Request(url, headers={"User-Agent": "Noetica-Scientific-Intelligence-V2"})
    results = []
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            for item in data.get("resultList", {}).get("result", [])[:max_results]:
                title = item.get("title", "")
                abstract = item.get("abstractText", "No abstract available.")
                
                # Extract assignees or inventors if available
                authors = []
                for auth in item.get("authorList", {}).get("author", []):
                    authors.append(auth.get("fullName", auth.get("lastName", "")))
                if not authors:
                    authors = ["Unknown Inventor/Assignee"]
                
                pub_date = item.get("firstPublicationDate", datetime.today().isoformat())
                
                results.append({
                    "id": f"pat_{item.get('id', 'unknown')}",
                    "title": f"[PATENT] {title}",
                    "abstract": abstract,
                    "authors": authors[:3],
                    "source": "Europe PMC (Patents)",
                    "domain": "Applied Technology / Patent",
                    "date": pub_date,
                    "url": f"https://europepmc.org/article/PAT/{item.get('id', '')}"
                })
    except Exception as e:
        print(f"⚠️ Patent Fetch Error for '{query}': {e}")
        
    return results


# ─────────────────────────────────────────────
# SEMANTIC SCHOLAR API (CONFERENCE PROCEEDINGS)
# ─────────────────────────────────────────────

def fetch_conferences(venue: str, max_results: int = 3) -> List[Dict[str, Any]]:
    """Fetch recent conference proceedings via Semantic Scholar."""
    safe_venue = urllib.parse.quote(venue)
    url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={safe_venue}&fields=title,abstract,authors,year,url,venue&limit={max_results}"
    
    req = urllib.request.Request(url, headers={"User-Agent": "Noetica-Scientific-Intelligence-V2"})
    results = []
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            for item in data.get("data", []):
                title = item.get("title", "")
                abstract = item.get("abstract", "No abstract available.")
                
                authors = [a.get("name", "") for a in item.get("authors", [])]
                if not authors:
                    authors = ["Unknown Author"]
                
                results.append({
                    "id": f"ss_{item.get('paperId', 'unknown')}",
                    "title": f"[CONFERENCE] {title}",
                    "abstract": abstract,
                    "authors": authors[:3],
                    "source": item.get("venue", venue),
                    "domain": "Conference Proceedings",
                    "date": datetime.date(item.get("year", datetime.date.today().year), 1, 1).isoformat(),
                    "url": item.get("url", "")
                })
    except Exception as e:
        print(f"⚠️ Conference Fetch Error for '{venue}': {e}")
        
    return results


# ─────────────────────────────────────────────
# CRUNCHBASE API (STARTUP FUNDING)
# ─────────────────────────────────────────────
import os
CRUNCHBASE_API_KEY = os.environ.get("CRUNCHBASE_API_KEY", "")

def fetch_crunchbase(query: str, max_results: int = 3) -> List[Dict[str, Any]]:
    """Fetch startup funding rounds matching scientific domains."""
    if not CRUNCHBASE_API_KEY:
        print(f"⚠️ Crunchbase API Key missing. Skipping real funding data for '{query}'.")
        return []

    # Requires paid API key for /v3.1/organizations. We use an abstracted proxy endpoint pattern here.
    safe_query = urllib.parse.quote(query)
    url = f"https://api.crunchbase.com/api/v4/searches/organizations"
    
    payload = {
        "field_ids": ["identifier", "short_description", "funding_total", "last_funding_at"],
        "query": [{"type": "predicate", "field_id": "short_description", "operator_id": "contains", "values": [query]}],
        "limit": max_results
    }
    
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), method="POST")
    req.add_header("X-cb-user-key", CRUNCHBASE_API_KEY)
    req.add_header("Content-Type", "application/json")
    
    results = []
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            for item in data.get("entities", []):
                props = item.get("properties", {})
                title = props.get("identifier", {}).get("value", "Unknown Startup")
                desc = props.get("short_description", "")
                funding = props.get("funding_total", {}).get("value_usd", 0)
                date = props.get("last_funding_at", datetime.today().isoformat())
                
                results.append({
                    "id": f"cb_{item.get('uuid', 'unknown')}",
                    "title": f"[STARTUP FUNDING] {title} raised ${funding}",
                    "abstract": desc,
                    "authors": [title],
                    "source": "Crunchbase",
                    "domain": "Venture Capital",
                    "date": date,
                    "url": f"https://www.crunchbase.com/organization/{props.get('identifier', {}).get('permalink', '')}"
                })
    except Exception as e:
        print(f"⚠️ Crunchbase Fetch Error for '{query}': {e}")
        
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
