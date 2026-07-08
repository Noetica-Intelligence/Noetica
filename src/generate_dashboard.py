"""
Noetica Web Dashboard Generator (V2)
Builds a static JSON payload for the 31x5 paradigm matrix.
Includes all fields needed for feature-parity with the email digest:
source, pdf_url, status, strategic_implication, knowledge_graph_edge,
source_types, NET sub-scores, and a proper 0-10 composite score.
"""

import json
import random
from pathlib import Path
from dashboard_config import PARADIGMS, DISCOVERY_TYPES

# ─────────────────────────────────────────────
# MOCK DATA POOLS (used only for empty cells)
# ─────────────────────────────────────────────

MOCK_TITLES = {
    "Patents / Clinical Trials": [
        "Phase III Trial of Novel Kinase Inhibitor",
        "Patent for Quantum Dot Photovoltaics",
        "Clinical Validation of mRNA Vector",
    ],
    "Research Grants / Startup Funding": [
        "$15M Series A for Next-Gen Biotech",
        "NSF Grant for High-Temperature Superconductors",
        "Seed Funding for Neural Interface Startup",
    ],
    "Scientific Datasets / Technical Reports": [
        "Global Climate Assessment Report 2026",
        "Open Dataset of 100M Protein Structures",
        "Technical Survey of 6G Telecommunications",
    ],
    "Open Source Projects / Software": [
        "v2.0 Release of Tensor Analytics Engine",
        "Open Source DNA Sequencing Library",
        "Physics Simulator for Rust",
    ],
}

MOCK_SOURCES = {
    "Research Papers / Preprints": ["arXiv", "PubMed", "bioRxiv", "Nature", "Science"],
    "Patents / Clinical Trials": ["USPTO", "ClinicalTrials.gov", "EPO"],
    "Research Grants / Startup Funding": ["NIH RePORTER", "NSF", "Crunchbase"],
    "Scientific Datasets / Technical Reports": ["Zenodo", "Figshare", "WHO"],
    "Open Source Projects / Software": ["GitHub", "GitLab", "PyPI"],
}


def generate_dashboard():
    kb_path = Path("data") / "knowledge_base.json"
    papers = []
    if kb_path.exists():
        with open(kb_path, "r", encoding="utf-8") as f:
            papers = json.load(f)

    # Sort existing papers by composite score (0-10 scale)
    papers = sorted(papers, key=lambda x: x.get("composite_score", 0), reverse=True)

    def map_source_to_dtype(source_types):
        if not source_types:
            return "Research Papers / Preprints"
        
        stype = source_types[0] if isinstance(source_types, list) else list(source_types.keys())[0] if isinstance(source_types, dict) else "paper"
        if stype in ("patent", "trial"):
            return "Patents / Clinical Trials"
        elif stype in ("grant", "funding"):
            return "Research Grants / Startup Funding"
        elif stype == "repo":
            return "Open Source Projects / Software"
        elif stype in ("dataset", "report"):
            return "Scientific Datasets / Technical Reports"
        else:
            return "Research Papers / Preprints"

    # Initialize the 31x5 matrix
    matrix = {p: {dt: None for dt in DISCOVERY_TYPES} for p in PARADIGMS}

    # ─────────────────────────────────────────────
    # POPULATE WITH REAL DATA
    # ─────────────────────────────────────────────
    for p in papers:
        domain = p.get("domain", "Other")
        if domain not in PARADIGMS:
            domain = "Other"
        
        dtype = map_source_to_dtype(p.get("source_types", ["paper"]))
        
        # First item placed is the highest-scoring for that cell (pre-sorted)
        if matrix[domain][dtype] is None:
            scores = p.get("scores", {})
            
            # Compute source aggregation string
            st_data = p.get("source_types")
            if isinstance(st_data, dict):
                parts = [f"{count} {name}{'s' if count > 1 else ''}" for name, count in st_data.items()]
                source_agg = ", ".join(parts) if parts else p.get("source", "")
            elif isinstance(st_data, list) and st_data:
                source_agg = ", ".join(f"1 {s}" for s in st_data)
            else:
                source_agg = p.get("source", "")

            matrix[domain][dtype] = {
                "title": p.get("title", ""),
                "authors": ", ".join((p.get("authors") or [])[:3]),
                "abstract": p.get("abstract", "")[:300] + ("..." if len(p.get("abstract", "")) > 300 else ""),
                "url": p.get("url", "#"),
                "pdf_url": p.get("pdf_url", ""),
                "source": p.get("source", ""),
                "source_agg": source_agg,
                "score": round(scores.get("composite", p.get("composite_score", 0)), 1),
                "novelty": round(scores.get("novelty", 0), 1),
                "evidence": round(scores.get("evidence", 0), 1),
                "trend": round(scores.get("recency", 0), 1),
                "status": p.get("status", "Emerging Signal"),
                "strategic_implication": p.get("strategic_implication", ""),
                "knowledge_graph_edge": p.get("knowledge_graph_edge", ""),
                "domain": domain,
                "date": p.get("date", "")[:10],
                "is_mock": False
            }

    # ─────────────────────────────────────────────
    # FILL EMPTY CELLS WITH MOCK DATA (0-10 scale)
    # ─────────────────────────────────────────────
    for p_name in PARADIGMS:
        for dt in DISCOVERY_TYPES:
            if matrix[p_name][dt] is None:
                if dt == "Research Papers / Preprints":
                    title = f"Advances in {p_name} Research"
                else:
                    title = random.choice(MOCK_TITLES[dt])

                mock_score = round(random.uniform(5.5, 9.5), 1)
                mock_novelty = round(random.uniform(5.0, 10.0), 1)
                mock_evidence = round(random.uniform(5.0, 10.0), 1)
                mock_trend = round(random.uniform(5.0, 10.0), 1)
                mock_source = random.choice(MOCK_SOURCES[dt])

                status = "Emerging Signal"
                if mock_score >= 8.5:
                    status = "Breakthrough Signal"
                elif mock_score >= 7.5:
                    status = "Strong Signal"

                matrix[p_name][dt] = {
                    "title": title,
                    "authors": "Various Contributors" if dt != "Research Papers / Preprints" else "Dr. Smith et al.",
                    "abstract": f"This is an illustrative entry representing the highest-scoring discovery in {p_name} under the category of {dt}. It demonstrates the Noetica scoring engine's capability to surface critical breakthroughs across all scientific disciplines.",
                    "url": "#",
                    "pdf_url": "",
                    "source": mock_source,
                    "source_agg": f"1 {mock_source}",
                    "score": mock_score,
                    "novelty": mock_novelty,
                    "evidence": mock_evidence,
                    "trend": mock_trend,
                    "status": status,
                    "strategic_implication": f"Consolidates existing empirical frameworks within {p_name}. Demonstrates moderate theoretical confidence; early-stage validation.",
                    "knowledge_graph_edge": f"Primary convergence vector linking {p_name} frameworks with adjacent disciplinary architecture.",
                    "domain": p_name,
                    "date": "",
                    "is_mock": True
                }

    out_dir = Path("docs")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    json_path = out_dir / "dashboard_data.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"paradigms": PARADIGMS, "types": DISCOVERY_TYPES, "matrix": matrix}, f, indent=2)
    
    print(f"[OK] Dashboard JSON matrix generated at {json_path}")

if __name__ == "__main__":
    generate_dashboard()
