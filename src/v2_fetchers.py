import urllib.request
import urllib.error
import urllib.parse
import json
import re
import hashlib
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
    if s is None:
        return ""
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
            clean = _sanitize_string(lst)
            return [clean] if clean else ["Unknown"]
        return ["Unknown"]
    cleaned = [_sanitize_string(i) for i in lst if i is not None and _sanitize_string(i)]
    return cleaned or ["Unknown"]

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
            title = _sanitize_string(item.get("project_title") or "Untitled Grant")
            abstract = _sanitize_string(item.get("abstract_text") or "")
            org_obj = item.get("organization") or {}
            org = _sanitize_string(org_obj.get("org_name") or "Unknown Org")

            pi_list = item.get("principal_investigators") or []
            raw_pi = pi_list[0].get("pi_name") if pi_list and isinstance(pi_list[0], dict) else ""
            pi = _sanitize_string(raw_pi) or "Unknown PI"

            cost = item.get("award_amount") or 0
            start_date = _sanitize_string(item.get("project_start_date")) or datetime.date.today().isoformat()

            results.append({
                "id": f"nih_{item.get('appl_id')}",
                "title": f"[GRANT] {title}",
                "abstract": abstract if abstract else f"Grant awarded to {org} for ${cost}",
                "authors": [pi],
                "source": "NIH RePORTER",
                "domain": "Biomedical Funding",
                "date": start_date,
                "url": f"https://reporter.nih.gov/project-details/{item.get('appl_id')}",
                "funding_amount": cost,
                "source_types": ["grant"]
            })
    except Exception as e:
        print(f"⚠️ NIH Fetch Error for '{query}': {e}")
        
    return results

# ─────────────────────────────────────────────
# GITHUB API (OPEN SOURCE INTELLIGENCE)
# ─────────────────────────────────────────────

def fetch_github_repos(topic: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """Fetch newly trending repositories from GitHub API with token-aware throttling."""
    since_30d = (datetime.date.today() - datetime.timedelta(days=30)).isoformat()
    safe_topic = urllib.parse.quote(topic)
    url = f"https://api.github.com/search/repositories?q={safe_topic}+created:>{since_30d}+stars:>5&sort=stars&order=desc&per_page={max_results}"
    
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
        items = data.get("items", [])
        if not items:
            # Fallback to recently pushed repos if strict 30d created filter is empty
            fallback_url = f"https://api.github.com/search/repositories?q={safe_topic}+stars:>25&sort=updated&order=desc&per_page={max_results}"
            req_fb = urllib.request.Request(fallback_url, headers={"User-Agent": "Noetica-Scientific-Intelligence-V2"})
            if github_token:
                req_fb.add_header("Authorization", f"Bearer {github_token}")
            data = robust_fetch_json(req_fb)
            items = data.get("items", [])
        for item in items:
            title = _sanitize_string(item.get("full_name") or "")
            desc = _sanitize_string(item.get("description")) or "Open-source scientific repository."
            author = _sanitize_string((item.get("owner") or {}).get("login")) or "Unknown"

            results.append({
                "id": f"gh_{item.get('id')}",
                "title": f"[REPO] {title}",
                "abstract": desc,
                "authors": [author],
                "source": "GitHub",
                "domain": "Open Source Software",
                "date": _sanitize_string(item.get("updated_at")) or datetime.date.today().isoformat(),
                "url": item.get("html_url") or "",
                "stars": item.get("stargazers_count") or 0,
                "source_types": ["repo"]
            })
    except Exception as e:
        print(f"⚠️ GitHub Fetch Error for '{topic}': {e}")
        
    return results

# ─────────────────────────────────────────────
# EUROPE PMC API (PATENT INTELLIGENCE)
# ─────────────────────────────────────────────

def fetch_patents(query: str, max_results: int = 3) -> List[Dict[str, Any]]:
    """Fetch patents via Europe PMC REST API with fast pageSize cap & retry tolerance."""
    safe_query = urllib.parse.quote(query)
    url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=SRC:PAT%20AND%20({safe_query})&format=json&resultType=core&pageSize={max_results}"
    
    req = urllib.request.Request(url, headers={"User-Agent": "Noetica-Scientific-Intelligence-V2"})
    results = []
    try:
        data = robust_fetch_json(req, timeout=15, max_retries=2)
        for item in data.get("resultList", {}).get("result", [])[:max_results]:
            title = _sanitize_string(item.get("title") or "")
            if not title:
                continue
            abstract = _sanitize_string(item.get("abstractText")) or "No abstract available."

            authors = []
            for auth in ((item.get("authorList") or {}).get("author") or []):
                name = _sanitize_string(auth.get("fullName") or auth.get("lastName"))
                if name:
                    authors.append(name)
            if not authors:
                authors = ["Unknown Inventor/Assignee"]

            pub_date = _sanitize_string(item.get("firstPublicationDate")) or datetime.date.today().isoformat()

            results.append({
                "id": f"pat_{item.get('id', 'unknown')}",
                "title": f"[PATENT] {title}",
                "abstract": abstract,
                "authors": authors[:3],
                "source": "Europe PMC (Patents)",
                "domain": "Applied Technology / Patent",
                "date": pub_date,
                "url": f"https://europepmc.org/article/PAT/{item.get('id', '')}",
                "source_types": ["patent"]
            })
    except Exception as e:
        print(f"⚠️ Patent Fetch Error for '{query}': {e}")
        
    return results


# ─────────────────────────────────────────────
# OPENALEX FLAGSHIP JOURNALS & CONFERENCES
# ─────────────────────────────────────────────

def fetch_conferences(venue: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """Fetch recent peer-reviewed journal/conference articles via OpenAlex (zero 429)."""
    since = (datetime.date.today() - datetime.timedelta(days=45)).isoformat()
    if venue.startswith("issn:"):
        issn_filter = f"primary_location.source.issn:{venue.split(':', 1)[1]}"
        url = (
            f"https://api.openalex.org/works?"
            f"filter={issn_filter},from_publication_date:{since},type:article,has_abstract:true"
            f"&sort=publication_date:desc&per-page={max_results}&mailto=research@example.com"
        )
    else:
        safe_venue = urllib.parse.quote(venue)
        url = (
            f"https://api.openalex.org/works?"
            f"filter=from_publication_date:{since},type:article|preprint,has_abstract:true"
            f"&search={safe_venue}&sort=publication_date:desc&per-page={max_results}&mailto=research@example.com"
        )

    req = urllib.request.Request(url, headers={"User-Agent": "Noetica-Scientific-Intelligence-V2"})
    results = []
    try:
        data = robust_fetch_json(req, timeout=15)
        for w in data.get("results", [])[:max_results]:
            title = _sanitize_string(w.get("title"))
            if not title:
                continue
            abstract_inv = w.get("abstract_inverted_index") or {}
            abstract = ""
            if abstract_inv:
                word_pos = {pos: word for word, positions in abstract_inv.items() for pos in positions}
                abstract = _sanitize_string(" ".join(word_pos[i] for i in sorted(word_pos))[:800])
            authors = [
                _sanitize_string((a.get("author") or {}).get("display_name"))
                for a in (w.get("authorships") or [])[:4]
                if (a.get("author") or {}).get("display_name")
            ] or ["Unknown Author"]
            src_name = _sanitize_string(
                ((w.get("primary_location") or {}).get("source") or {}).get("display_name")
            ) or venue
            doi = w.get("doi") or ""
            landing = ((w.get("primary_location") or {}).get("landing_page_url")
                       or (w.get("open_access") or {}).get("oa_url")
                       or doi or "")
            oa_pdf = (w.get("open_access") or {}).get("oa_url") or ""
            results.append({
                "id": _sanitize_string(w.get("id")) or f"oa_conf_{len(results)}",
                "title": title,
                "abstract": abstract or f"Peer-reviewed article published in {src_name}.",
                "authors": authors,
                "source": src_name,
                "domain": venue if not venue.startswith("issn:") else src_name,
                "date": _sanitize_string(w.get("publication_date")) or datetime.date.today().isoformat(),
                "url": landing,
                "pdf_url": oa_pdf,
                "cited_by": w.get("cited_by_count") or 0,
                "source_types": ["paper"],
            })
    except Exception as e:
        print(f"⚠️ Conference/Venue Fetch Error for '{venue}': {e}")

    return results


# ─────────────────────────────────────────────
# SCIENTIFIC DATASETS & TECHNICAL REPORTS (ZENODO + HUGGINGFACE)
# ─────────────────────────────────────────────

def fetch_datasets(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """Fetch recent scientific datasets from Zenodo and HuggingFace Datasets API."""
    results: List[Dict[str, Any]] = []
    safe_q = urllib.parse.quote(query)

    # 1. Zenodo open research datasets
    zenodo_url = f"https://zenodo.org/api/records?q={safe_q}&type=dataset&sort=mostrecent&size={max_results}"
    req_z = urllib.request.Request(zenodo_url, headers={"User-Agent": "Noetica-Scientific-Intelligence-V2"})
    try:
        zdata = robust_fetch_json(req_z, timeout=12, max_retries=2)
        for hit in (zdata.get("hits") or {}).get("hits", [])[:max_results]:
            meta = hit.get("metadata") or {}
            title = _sanitize_string(meta.get("title"))
            if not title:
                continue
            raw_desc = re.sub(r"<[^>]+>", " ", meta.get("description") or "").strip()
            desc = _sanitize_string(raw_desc)[:700] or f"Scientific dataset deposited on Zenodo matching '{query}'."
            creators = [
                _sanitize_string(c.get("name"))
                for c in (meta.get("creators") or [])[:3]
                if c.get("name")
            ] or ["Zenodo Contributor"]
            links = hit.get("links") or {}
            rec_url = links.get("self_html") or hit.get("doi_url") or ""
            results.append({
                "id": f"zen_{hit.get('id', 'unknown')}",
                "title": f"[DATASET] {title}",
                "abstract": desc,
                "authors": creators,
                "source": "Zenodo Datasets",
                "domain": query.title(),
                "date": _sanitize_string(meta.get("publication_date")) or datetime.date.today().isoformat(),
                "url": rec_url,
                "pdf_url": "",
                "source_types": ["dataset"],
            })
    except Exception as e:
        print(f"⚠️ Zenodo Dataset Fetch Error for '{query}': {e}")

    # 2. HuggingFace Datasets
    hf_url = f"https://huggingface.co/api/datasets?search={safe_q}&sort=downloads&direction=-1&limit={max(2, max_results // 2)}"
    req_hf = urllib.request.Request(hf_url, headers={"User-Agent": "Noetica-Scientific-Intelligence-V2"})
    try:
        hf_items = robust_fetch_json(req_hf, timeout=10, max_retries=2)
        if isinstance(hf_items, list):
            for item in hf_items[:max(2, max_results // 2)]:
                ds_id = _sanitize_string(item.get("id"))
                if not ds_id:
                    continue
                author = _sanitize_string(item.get("author")) or ds_id.split("/")[0]
                desc = _sanitize_string(item.get("description")) or f"Open scientific dataset hosted on HuggingFace ({ds_id})."
                downloads = item.get("downloads") or 0
                results.append({
                    "id": f"hf_{ds_id.replace('/', '_')}",
                    "title": f"[DATASET] {ds_id}",
                    "abstract": f"{desc[:550]} (Downloads: {downloads:,})",
                    "authors": [author],
                    "source": "HuggingFace Datasets",
                    "domain": "Artificial Intelligence",
                    "date": _sanitize_string(item.get("lastModified"))[:10] or datetime.date.today().isoformat(),
                    "url": f"https://huggingface.co/datasets/{ds_id}",
                    "pdf_url": "",
                    "source_types": ["dataset"],
                })
    except Exception as e:
        print(f"⚠️ HuggingFace Dataset Fetch Error for '{query}': {e}")

    return results


# ─────────────────────────────────────────────
# UNIFIED RSS AGGREGATOR (STARTUP FUNDING)
# ─────────────────────────────────────────────

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
                    "url": link,
                    "source_types": ["funding"]
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
