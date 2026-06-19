"""
Scientific Intelligence Engine — Scoring Engine
Ranks papers by novelty, impact, recency, and cross-disciplinary potential.
No social-media or popularity-based ranking. Evidence-first.
"""

import re
import math
import datetime


# ─────────────────────────────────────────────
# BREAKTHROUGH SIGNAL KEYWORDS
# Empirically known terms that appear in high-impact papers
# ─────────────────────────────────────────────

BREAKTHROUGH_SIGNALS = [
    # Methods
    "novel", "first", "breakthrough", "state-of-the-art", "unprecedented",
    "outperforms", "surpasses", "revolutionize", "transformative",
    # Discovery types
    "we discover", "we demonstrate", "we prove", "we show",
    "new mechanism", "previously unknown", "first evidence",
    "generalizes", "unifies", "resolves",
    # Quantitative signals
    "significant improvement", "order of magnitude", "10x", "100x",
    "new record", "highest reported", "lowest reported",
    # Interdisciplinary
    "cross-disciplinary", "bridges", "connecting", "unifying",
    "applies to", "applicable across",
]

HYPE_PENALTIES = [
    "we believe", "might", "could potentially", "preliminary",
    "in theory", "hypothesize", "speculate", "further study needed",
    "not yet validated", "awaiting peer review",
]

METHODOLOGY_QUALITY = [
    "randomized controlled trial", "systematic review", "meta-analysis",
    "n=", "cohort study", "blind study", "validated on",
    "benchmark", "ablation study", "statistical significance",
    "p-value", "confidence interval",
]

# Domain weights: domains with more cross-disciplinary influence get bonus
DOMAIN_INFLUENCE_WEIGHTS = {
    "AI & Machine Learning":  1.3,
    "Pure Mathematics":       1.2,
    "Theoretical Physics":    1.2,
    "Statistics":             1.15,
    "Bioinformatics":         1.15,
    "Quantum Computing":      1.2,
    "Systems Biology":        1.1,
    "Oncology":               1.1,
    "Circadian Biology":      1.05,
    "Neuroscience":           1.1,
    "Philosophy":             1.05,
    "Economics":              1.0,
    "default":                1.0,
}

# Domains with high cross-disciplinary connection potential
CROSS_DOMAIN_PAIRS = {
    "Quantum Computing":      ["Cryptography", "AI & Machine Learning", "Drug Discovery", "Optimization"],
    "AI & Machine Learning":  ["Drug Discovery", "Structural Biology", "Materials Science", "Economics", "Climate Science"],
    "Pure Mathematics":       ["AI & Machine Learning", "Cryptography", "Physics", "Statistics"],
    "Circadian Biology":      ["Oncology", "Neuroscience", "Pharmacology", "Systems Biology"],
    "Structural Biology":     ["Drug Discovery", "AI & Machine Learning", "Bioinformatics"],
    "Theoretical Physics":    ["Quantum Computing", "Mathematics", "Cosmology", "AI"],
    "Statistics":             ["AI & Machine Learning", "Epidemiology", "Economics", "Genetics"],
    "Synthetic Biology":      ["Drug Discovery", "Agriculture", "Materials Science", "Bioinformatics"],
}


# ─────────────────────────────────────────────
# SCORING FUNCTIONS
# ─────────────────────────────────────────────

def score_novelty(title: str, abstract: str) -> float:
    """
    Score 0–10: How novel/groundbreaking is this paper?
    Based on breakthrough keyword density minus hype penalties.
    """
    text = (title + " " + abstract).lower()
    signal_hits = sum(1 for kw in BREAKTHROUGH_SIGNALS if kw in text)
    hype_hits   = sum(1 for kw in HYPE_PENALTIES if kw in text)
    raw = min(signal_hits * 1.5, 10.0) - min(hype_hits * 0.5, 3.0)
    return max(0.0, min(10.0, raw))


def score_evidence(abstract: str) -> float:
    """
    Score 0–10: How strong is the experimental/empirical evidence?
    """
    text = abstract.lower()
    method_hits = sum(1 for kw in METHODOLOGY_QUALITY if kw in text)
    # Papers with numbers in abstract often have quantitative results
    numbers = len(re.findall(r'\b\d+\.?\d*[%±]\b|\bn\s*=\s*\d+', text))
    raw = min(method_hits * 2.0 + numbers * 0.5, 10.0)
    return max(0.0, min(10.0, raw))


def score_recency(date_str: str) -> float:
    """
    Score 0–10: Papers from today get 10, older papers decay logarithmically.
    """
    if not date_str:
        return 5.0
    try:
        # Handle partial dates like "2026-Jun-01"
        clean = date_str[:10].replace("Jan","01").replace("Feb","02").replace("Mar","03") \
                               .replace("Apr","04").replace("May","05").replace("Jun","06") \
                               .replace("Jul","07").replace("Aug","08").replace("Sep","09") \
                               .replace("Oct","10").replace("Nov","11").replace("Dec","12")
        pub_date = datetime.date.fromisoformat(clean)
    except ValueError:
        return 5.0
    delta_days = (datetime.date.today() - pub_date).days
    if delta_days < 0:
        return 10.0
    # Logarithmic decay: today=10, 7 days=7, 30 days=5, 90 days=3
    score = 10.0 - (2.5 * math.log1p(delta_days / 3))
    return max(0.0, min(10.0, score))


def score_citation_momentum(cited_by: int, days_old: int) -> float:
    """
    Score 0–10: Citation velocity (citations per day since publication).
    Only useful for OpenAlex/SemanticScholar which provide citation counts.
    """
    if cited_by <= 0 or days_old <= 0:
        return 0.0
    velocity = cited_by / max(days_old, 1)
    return min(velocity * 10, 10.0)


def score_domain_impact(domain: str) -> float:
    """
    Score: Multiplier based on how foundational/cross-disciplinary a domain is.
    """
    return DOMAIN_INFLUENCE_WEIGHTS.get(domain, DOMAIN_INFLUENCE_WEIGHTS["default"])


def get_cross_disciplinary_connections(domain: str) -> list[str]:
    """Return list of other domains this paper might impact."""
    return CROSS_DOMAIN_PAIRS.get(domain, [])


def score_title_quality(title: str) -> float:
    """
    Score 0–2 bonus: Penalize vague titles, reward specific ones.
    """
    words = title.split()
    if len(words) < 4:
        return 0.0
    has_colon = ":" in title  # "Method: A Study of..." style = specific
    has_numbers = any(c.isdigit() for c in title)
    specificity = (1.0 if has_colon else 0.0) + (0.5 if has_numbers else 0.0)
    length_bonus = min((len(words) - 4) * 0.05, 0.5)
    return min(specificity + length_bonus, 2.0)


# ─────────────────────────────────────────────
# SOURCE RELIABILITY ENGINE
# ─────────────────────────────────────────────

# Tiers: 1 (Highest) to 4 (Blogs/Media)
SOURCE_TIERS = {
    "Nature": 1.5, "Science": 1.5, "Cell": 1.5, "NEJM": 1.5, "Lancet": 1.5,
    "PubMed": 1.2, "SemanticScholar": 1.1, "OpenAlex": 1.1,
    "arXiv": 1.0, "bioRxiv": 1.0, "medRxiv": 1.0,
    "default": 1.0
}

def score_source_reliability(source_name: str) -> float:
    """Returns a multiplier based on the source's peer-review tier."""
    for key, mult in SOURCE_TIERS.items():
        if key.lower() in source_name.lower():
            return mult
    return SOURCE_TIERS["default"]

# ─────────────────────────────────────────────
# COMPOSITE SCORING
# ─────────────────────────────────────────────

def compute_composite_score(paper: dict) -> dict:
    """
    Compute all sub-scores and a final composite score for a discovery.
    Returns the discovery dict enriched with scoring data and ranking explanations.
    """
    title    = paper.get("title", "")
    abstract = paper.get("abstract", "")
    domain   = paper.get("domain", "")
    date_str = paper.get("date", "")
    source   = paper.get("source", "Unknown")
    cited_by = int(paper.get("cited_by", 0) or 0)

    # Compute days old
    try:
        clean = date_str[:10]
        pub_date = datetime.date.fromisoformat(clean)
        days_old = max((datetime.date.today() - pub_date).days, 1)
    except (ValueError, TypeError):
        days_old = 7

    # Sub-scores
    novelty     = score_novelty(title, abstract)
    evidence    = score_evidence(abstract)
    recency     = score_recency(date_str)
    citation_v  = score_citation_momentum(cited_by, days_old)
    
    # Multipliers
    domain_mult = score_domain_impact(domain)
    source_mult = score_source_reliability(source)
    title_bonus = score_title_quality(title)

    # Weighted composite (out of 10)
    raw_composite = (
        novelty  * 0.35 +
        evidence * 0.35 +
        recency  * 0.15 +
        citation_v * 0.15
    )

    # Apply multipliers
    composite = min(raw_composite * domain_mult * source_mult + title_bonus * 0.2, 10.0)

    # Cross-disciplinary connections
    cross_domains = get_cross_disciplinary_connections(domain)

    # Explanation Engine
    explanation = {
        "Evidence Strength": f"{evidence:.1f}/10",
        "Novelty": f"{novelty:.1f}/10",
        "Source Reliability": f"x{source_mult:.1f} ({source})",
        "Cross-Field Impact": f"x{domain_mult:.2f} ({len(cross_domains)} domains)",
    }

    # Discovery Lifecycle Status
    status = "Emerging"
    if composite > 8.5:
        status = "Breakthrough"
    elif composite > 7.0:
        status = "Growing"

    paper["scores"] = {
        "novelty":     round(novelty, 2),
        "evidence":    round(evidence, 2),
        "recency":     round(recency, 2),
        "citation_v":  round(citation_v, 2),
        "composite":   round(composite, 2),
    }
    paper["explanation"] = explanation
    paper["status"] = status
    paper["cross_disciplinary"] = cross_domains
    paper["days_old"] = days_old
    return paper


# ─────────────────────────────────────────────
# BATCH SCORER + RANKER
# ─────────────────────────────────────────────

def score_and_rank(papers: list[dict], top_n: int = 15) -> list[dict]:
    """
    Score all papers and return top_n ranked by composite score.
    Ensures domain diversity: at most 3 papers per domain in top results.
    """
    scored = [compute_composite_score(p) for p in papers]
    scored.sort(key=lambda p: p["scores"]["composite"], reverse=True)

    # Domain-diverse selection
    domain_counts: dict[str, int] = {}
    diverse_top: list[dict] = []
    remainder:   list[dict] = []

    for p in scored:
        d = p.get("domain", "Other")
        if domain_counts.get(d, 0) < 3:
            domain_counts[d] = domain_counts.get(d, 0) + 1
            diverse_top.append(p)
        else:
            remainder.append(p)
        if len(diverse_top) >= top_n:
            break

    # Fill to top_n if needed
    needed = top_n - len(diverse_top)
    if needed > 0:
        diverse_top.extend(remainder[:needed])

    return diverse_top


if __name__ == "__main__":
    import json
    from pathlib import Path
    import sys

    # Test with a small mock dataset
    mock = [
        {
            "title": "AlphaFold3 Predicts Protein Complexes: A Novel Approach",
            "abstract": "We demonstrate unprecedented accuracy in predicting protein-ligand complexes. Our method outperforms all previous state-of-the-art methods by 23%. Validated on n=500 benchmark structures. Statistical significance p<0.001.",
            "domain": "Structural Biology",
            "date": datetime.date.today().isoformat(),
            "cited_by": 42,
            "source": "arXiv",
            "url": "https://arxiv.org/abs/2501.00001",
            "id": "2501.00001",
            "authors": ["Doe J", "Smith A"],
            "pdf_url": "",
        },
        {
            "title": "Quantum Error Correction Breakthrough",
            "abstract": "First demonstration of fault-tolerant quantum computing at scale. We show that logical qubit error rates can be reduced by an order of magnitude. Our results suggest we have resolved a key barrier to practical quantum computing.",
            "domain": "Quantum Computing",
            "date": (datetime.date.today() - datetime.timedelta(days=2)).isoformat(),
            "cited_by": 18,
            "source": "arXiv",
            "url": "https://arxiv.org/abs/2501.00002",
            "id": "2501.00002",
            "authors": ["Lee K"],
            "pdf_url": "",
        },
    ]
    ranked = score_and_rank(mock, top_n=5)
    for i, p in enumerate(ranked, 1):
        print(f"\n#{i} [{p['scores']['composite']:.1f}/10] {p['title'][:70]}")
        print(f"   Scores: {p['scores']}")
        print(f"   Cross-domain: {p['cross_disciplinary']}")
