import urllib.request
import urllib.error
import urllib.parse
import json
import time
import os
import datetime
from typing import List, Dict, Any
import xml.etree.ElementTree as ET

# ─────────────────────────────────────────────
# ROBUST NETWORK & SANITIZATION UTILS
# ─────────────────────────────────────────────

def _sanitize_string(s: Any) -> str:
    """UTF-8 sanitization and schema enforcement (ensures output is a clean string)."""
    if not isinstance(s, str):
        try:
            s = str(s)
        except Exception:
            return ""
    # Strip null bytes and non-printable control chars that break strict JSON parsers (Zig)
    return "".join(c for c in s if c.isprintable() or c in '\n\r\t')

def _sanitize_list(lst: Any) -> List[str]:
    """Schema enforcement for lists of strings (e.g. authors)."""
    if not isinstance(lst, list):
        if isinstance(lst, str):
            return [_sanitize_string(lst)]
        return ["Unknown"]
    return [_sanitize_string(i) for i in lst if i]

def robust_fetch_json(req: urllib.request.Request, timeout: int = 10, max_retries: int = 3) -> dict:
    """Executes an HTTP request with exponential backoff, retries on 429/5xx, and strict timeouts."""
    import socket
    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                # Use errors='replace' to sanitize invalid UTF-8 byte sequences at the transport layer
                raw_data = response.read().decode('utf-8', errors='replace')
                if not raw_data:
                    return {}
                return json.loads(raw_data)
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504):
                time.sleep((2 ** attempt) + 1.5)  # Exponential backoff
                continue
            else:
                raise
        except (urllib.error.URLError, socket.timeout, ConnectionResetError) as e:
            if attempt == max_retries - 1:
                print(f"    [!] Max retries reached or fatal error: {e}")
                return {}
            time.sleep((2 ** attempt) + 1.5)
        except json.JSONDecodeError:
            print("    [!] Corrupted JSON payload received.")
            return {}
    return {}

def robust_fetch_xml(req: urllib.request.Request, timeout: int = 10, max_retries: int = 3) -> str:
    """Fetches raw XML data with the same robust backoff."""
    import socket
    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return response.read().decode('utf-8', errors='replace')
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504):
                time.sleep((2 ** attempt) + 1.5)
                continue
            else:
                return ""
        except (urllib.error.URLError, socket.timeout, ConnectionResetError):
            if attempt == max_retries - 1:
                return ""
            time.sleep((2 ** attempt) + 1.5)
    return ""


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
        data = robust_fetch_json(req)
        for item in data.get("results", []):
            title = _sanitize_string(item.get("project_title", ""))
            abstract = _sanitize_string(item.get("abstract_text", ""))
            org = _sanitize_string(item.get("organization", {}).get("org_name", "Unknown Org"))
            
            pi_list = item.get("principal_investigators", [])
            pi = _sanitize_string(pi_list[0].get("pi_name") if pi_list else "Unknown")
            
            cost = item.get("award_amount", 0)
            
            results.append({
                "id": f"nih_{item.get('appl_id')}",
                "title": f"[GRANT] {title}",
                "abstract": abstract if abstract else f"Grant awarded to {org} for ${cost}",
                "authors": [pi],
                "source": "NIH RePORTER",
                "domain": "Biomedical Funding",
                "date": item.get("project_start_date", datetime.date.today().isoformat()),
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
    """Fetch trending repositories from GitHub API with token-aware throttling."""
    safe_topic = urllib.parse.quote(topic)
    url = f"https://api.github.com/search/repositories?q={safe_topic}+stars:>50&sort=updated&order=desc&per_page={max_results}"
    
    req = urllib.request.Request(url, headers={"User-Agent": "Noetica-Scientific-Intelligence-V2"})
    
    # Token-Aware Rate Limiting
    github_token = os.environ.get("GITHUB_TOKEN")
    if github_token:
        req.add_header("Authorization", f"Bearer {github_token}")
    else:
        time.sleep(6.1) # Throttle to < 10 req/min globally to be safe
    
    results = []
    try:
        data = robust_fetch_json(req)
        for item in data.get("items", []):
            title = _sanitize_string(item.get("full_name", ""))
            desc = _sanitize_string(item.get("description", "No description provided."))
            author = _sanitize_string(item.get("owner", {}).get("login", "Unknown"))
            
            results.append({
                "id": f"gh_{item.get('id')}",
                "title": f"[REPO] {title}",
                "abstract": desc,
                "authors": [author],
                "source": "GitHub",
                "domain": "Open Source Software",
                "date": item.get("updated_at", datetime.date.today().isoformat()),
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
    url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=SRC:PAT%20AND%20({safe_query})&format=json&resultType=core"
    
    req = urllib.request.Request(url, headers={"User-Agent": "Noetica-Scientific-Intelligence-V2"})
    results = []
    try:
        data = robust_fetch_json(req)
        for item in data.get("resultList", {}).get("result", [])[:max_results]:
            title = _sanitize_string(item.get("title", ""))
            abstract = _sanitize_string(item.get("abstractText", "No abstract available."))
            
            authors = []
            for auth in item.get("authorList", {}).get("author", []):
                authors.append(_sanitize_string(auth.get("fullName", auth.get("lastName", ""))))
            if not authors:
                authors = ["Unknown Inventor/Assignee"]
            
            pub_date = item.get("firstPublicationDate", datetime.date.today().isoformat())
            
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
        data = robust_fetch_json(req)
        for item in data.get("data", []):
            title = _sanitize_string(item.get("title", ""))
            abstract = _sanitize_string(item.get("abstract", "No abstract available."))
            
            authors = [_sanitize_string(a.get("name", "")) for a in item.get("authors", [])]
            if not authors:
                authors = ["Unknown Author"]
            
            year = item.get("year", datetime.date.today().year)
            if not year: year = datetime.date.today().year
            v = _sanitize_string(item.get("venue", venue))
            if not v: v = venue
            
            results.append({
                "id": f"ss_{item.get('paperId', 'unknown')}",
                "title": f"[CONFERENCE] {title}",
                "abstract": abstract,
                "authors": authors[:3],
                "source": v,
                "domain": "Conference Proceedings",
                "date": datetime.date(year, 1, 1).isoformat(),
                "url": item.get("url", "")
            })
    except Exception as e:
        print(f"⚠️ Conference Fetch Error for '{venue}': {e}")
        
    return results


# ─────────────────────────────────────────────
# UNIFIED RSS AGGREGATOR (STARTUP FUNDING)
# ─────────────────────────────────────────────
import re
import hashlib

def fetch_startup_funding_rss(query: str, max_results: int = 3) -> List[Dict[str, Any]]:
    """Fetch startup funding rounds using unified RSS aggregation (Google News + TechCrunch)."""
    safe_query = urllib.parse.quote(f"{query} startup funding raise")
    
    # Global unified net
    feeds = [
        f"https://news.google.com/rss/search?q={safe_query}&hl=en-US&gl=US&ceid=US:en",
        "https://techcrunch.com/category/fundings-exits/feed/"
    ]
    
    results = []
    seen_titles = set()
    
    for feed_url in feeds:
        req = urllib.request.Request(feed_url, headers={"User-Agent": "Noetica-Scientific-Intelligence-V2"})
        try:
            xml_data = robust_fetch_xml(req)
            if not xml_data:
                continue
            
            root = ET.fromstring(xml_data)
            
            for item in root.findall(".//item"):
                title = _sanitize_string(item.findtext("title", ""))
                link = item.findtext("link", "")
                desc = _sanitize_string(item.findtext("description", ""))
                pub_date = item.findtext("pubDate", datetime.date.today().isoformat())
                
                # Ensure relevance for global generic feeds
                if "techcrunch" in feed_url:
                    if query.lower() not in title.lower() and query.lower() not in desc.lower():
                        continue
                        
                if title in seen_titles:
                    continue
                seen_titles.add(title)
                
                clean_desc = re.sub('<[^<]+>', '', desc).strip()
                if len(clean_desc) > 300:
                    clean_desc = clean_desc[:300] + "..."
                    
                doc_id = "rss_" + hashlib.md5(link.encode()).hexdigest()[:10]
                
                results.append({
                    "id": doc_id,
                    "title": f"[STARTUP FUNDING] {title}",
                    "abstract": clean_desc,
                    "authors": ["Venture News"],
                    "source": "Aggregated VC Feeds",
                    "domain": "Venture Capital",
                    "date": pub_date,
                    "url": link
                })
                
                if len(results) >= max_results:
                    break
        except Exception as e:
            print(f"⚠️ RSS Fetch Error for '{feed_url}': {e}")
            
        if len(results) >= max_results:
            break
            
    return results[:max_results]


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
