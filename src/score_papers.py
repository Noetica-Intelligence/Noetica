"""
Scientific Intelligence Engine — Scoring Engine
Ranks papers by novelty, impact, recency, and cross-disciplinary potential.
Outputs a 0-100 score and narrative AI rationale.
"""

import re
import math
import datetime


# ─────────────────────────────────────────────
# BREAKTHROUGH SIGNAL KEYWORDS
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
    # Clinical / Bio
    "randomized controlled trial", "systematic review", "meta-analysis",
    "n=", "cohort study", "blind study", "validated on",
    "benchmark", "ablation study", "statistical significance",
    "p-value", "confidence interval",
    # Physics / Math / CS / Chemistry
    "theorem", "proof", "simulation", "accuracy", "state-of-the-art",
    "first-principles", "ab initio", "experimental observation",
    "rigorous", "computational model", "density functional theory",
    "topology", "manifold", "algorithm",
]

# Domain weights: domains with more cross-disciplinary influence get bonus
DOMAIN_INFLUENCE_WEIGHTS = {
    "AI & Machine Learning":  1.2,
    "Pure Mathematics":       1.15,
    "Theoretical Physics":    1.15,
    "Statistics":             1.1,
    "Bioinformatics":         1.1,
    "Quantum Computing":      1.15,
    "Systems Biology":        1.1,
    "Oncology":               1.05,
    "Circadian Biology":      1.05,
    "Neuroscience":           1.05,
    "Philosophy":             1.0,
    "Economics":              1.0,
    "default":                1.0,
}

# Domains with high cross-disciplinary connection potential
CROSS_DOMAIN_PAIRS = {
    "Quantum Computing":      ["Cryptography", "AI", "Drug Discovery", "Optimization"],
    "AI & Machine Learning":  ["Drug Discovery", "Structural Biology", "Materials Science", "Economics", "Mathematics"],
    "Pure Mathematics":       ["AI", "Cryptography", "Physics", "Statistics"],
    "Circadian Biology":      ["Oncology", "Neuroscience", "Pharmacology", "Systems Biology"],
    "Structural Biology":     ["Drug Discovery", "AI", "Bioinformatics"],
    "Theoretical Physics":    ["Quantum Computing", "Mathematics", "Cosmology", "AI"],
    "Experimental Physics":   ["Materials Science", "Quantum Computing", "Engineering"],
    "Statistics":             ["AI", "Epidemiology", "Economics", "Genetics"],
    "Synthetic Biology":      ["Drug Discovery", "Agriculture", "Materials Science", "Bioinformatics"],
    "Materials Science":      ["Quantum Computing", "Engineering", "Physics", "Chemistry"],
}


# ─────────────────────────────────────────────
# SCORING FUNCTIONS
# ─────────────────────────────────────────────

def score_novelty(title: str, abstract: str) -> float:
    """Score 0–10 based on breakthrough keywords minus hype."""
    text = ((title or "") + " " + (abstract or "")).lower()
    signal_hits = sum(1 for kw in BREAKTHROUGH_SIGNALS if kw in text)
    hype_hits   = sum(1 for kw in HYPE_PENALTIES if kw in text)
    # Base 5.0 for passing filters. Each hit gives +2.0.
    raw = min(5.0 + signal_hits * 2.0, 10.0) - min(hype_hits * 1.0, 3.0)
    return max(0.0, min(10.0, raw))


def score_evidence(abstract: str) -> float:
    """Score 0–10 based on experimental/theoretical methodology."""
    text = (abstract or "").lower()
    method_hits = sum(1 for kw in METHODOLOGY_QUALITY if kw in text)
    numbers = len(re.findall(r'\b\d+\.?\d*[%±]\b|\bn\s*=\s*\d+', text))
    # Base 5.0. Hits give strong boosts.
    raw = min(5.0 + method_hits * 2.5 + numbers * 0.5, 10.0)
    return max(0.0, min(10.0, raw))


def score_recency(date_str: str) -> float:
    """Score 0–10: Logarithmic decay."""
    if not date_str:
        return 8.0
    try:
        clean = date_str[:10].replace("Jan","01").replace("Feb","02").replace("Mar","03") \
                               .replace("Apr","04").replace("May","05").replace("Jun","06") \
                               .replace("Jul","07").replace("Aug","08").replace("Sep","09") \
                               .replace("Oct","10").replace("Nov","11").replace("Dec","12")
        pub_date = datetime.date.fromisoformat(clean)
    except ValueError:
        return 8.0
    delta_days = (datetime.date.today() - pub_date).days
    if delta_days <= 0:
        return 10.0
    score = 10.0 - (2.0 * math.log1p(delta_days / 3))
    return max(0.0, min(10.0, score))


def score_citation_momentum(cited_by: int, days_old: int) -> float:
    """Score 0–10: Citation velocity. No penalty for very new papers."""
    if days_old <= 7:
        return 10.0  # Grace period: brand new papers have maximum momentum potential
    if cited_by <= 0:
        return 4.0   # Base floor for older papers with 0 citations
    velocity = cited_by / max(days_old, 1)
    return min(4.0 + velocity * 10.0, 10.0)


def score_domain_impact(domain: str) -> float:
    return DOMAIN_INFLUENCE_WEIGHTS.get(domain, DOMAIN_INFLUENCE_WEIGHTS["default"])


def get_cross_disciplinary_connections(domain: str) -> list[str]:
    # Try exact match, otherwise try partial match
    if domain in CROSS_DOMAIN_PAIRS:
        return CROSS_DOMAIN_PAIRS[domain]
    for key, pairs in CROSS_DOMAIN_PAIRS.items():
        if key.lower() in domain.lower() or domain.lower() in key.lower():
            return pairs
    return []


def score_title_quality(title: str) -> float:
    """Bonus for specific titles."""
    words = title.split()
    if len(words) < 4:
        return 0.0
    has_colon = ":" in title
    has_numbers = any(c.isdigit() for c in title)
    specificity = (1.0 if has_colon else 0.0) + (0.5 if has_numbers else 0.0)
    length_bonus = min((len(words) - 4) * 0.05, 0.5)
    return min(specificity + length_bonus, 2.0)


def score_source_reliability(source_name: str) -> float:
    tiers = {
        "Nature": 1.3, "Science": 1.3, "Cell": 1.3, "NEJM": 1.3, "Lancet": 1.3,
        "PubMed": 1.1, "SemanticScholar": 1.05, "OpenAlex": 1.05,
        "arXiv": 1.0, "bioRxiv": 1.0, "medRxiv": 1.0,
    }
    for key, mult in tiers.items():
        if key.lower() in source_name.lower():
            return mult
    return 1.0


# ─────────────────────────────────────────────
# COMPOSITE SCORING
# ─────────────────────────────────────────────

def compute_composite_score(paper: dict) -> dict:
    title    = paper.get("title", "")
    abstract = paper.get("abstract", "")
    domain   = paper.get("domain", "")
    date_str = paper.get("date", "")
    source   = paper.get("source", "Unknown")
    cited_by = int(paper.get("cited_by", 0) or 0)

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
    
    domain_mult = score_domain_impact(domain)
    source_mult = score_source_reliability(source)
    title_bonus = score_title_quality(title)

    raw_composite = (
        novelty  * 0.35 +
        evidence * 0.35 +
        recency  * 0.15 +
        citation_v * 0.15
    )

    # Calculate 0-10 base
    base_10 = min(raw_composite * domain_mult * source_mult + title_bonus * 0.2, 10.0)
    
    # Map to 0-10 scale (final_score)
    final_score = round(base_10, 1)

    cross_domains = get_cross_disciplinary_connections(domain)

    # ─────────────────────────────────────────────
    # NEW: STRATEGIC IMPLICATION SYNTHESIS
    # ─────────────────────────────────────────────
    import random
    implications = []
    if novelty >= 8.0:
        implications.append(f"Challenges foundational assumptions within {domain}. High probability of paradigm shift.")
    elif novelty >= 6.0:
        implications.append(f"Introduces novel methodology to {domain}, expanding theoretical boundaries.")
    else:
        # Dynamic templates to avoid robotic repetition
        templates = [
            f"Consolidates existing empirical frameworks within {domain}.",
            f"Provides rigorous validation for ongoing {domain} research vectors.",
            f"Offers methodical advancement of established {domain} paradigms.",
            f"Demonstrates practical utility in applied {domain} contexts.",
            f"Strengthens the computational foundation of {domain} models."
        ]
        implications.append(random.choice(templates))
        
    if evidence >= 8.0:
        implications.append("Supported by rigorous mathematical/empirical architecture. Validation confidence is extremely high.")
    elif evidence >= 6.0:
        implications.append("Demonstrates moderate theoretical confidence; early-stage validation.")

    if source_mult > 1.1:
        implications.append("Signal amplified by premium source tier.")

    # ─────────────────────────────────────────────
    # NEW: KNOWLEDGE GRAPH EDGE SYNTHESIS
    # ─────────────────────────────────────────────
    kg_edge = ""
    if len(cross_domains) >= 1:
        # e.g. "Primary vector bridging Theoretical Physics with Quantum Computing methodologies."
        kg_edge = f"Primary convergence vector linking {domain} frameworks with {cross_domains[0]} architecture."
        if len(cross_domains) >= 2:
            kg_edge += f" Secondary resonance with {cross_domains[1]}."

    # Discovery Lifecycle Status
    status = "Emerging Signal"
    if final_score >= 8.5:
        status = "Breakthrough Signal"
    elif final_score >= 7.5:
        status = "Strong Signal"

    paper["scores"] = {
        "novelty":     round(novelty, 2),
        "evidence":    round(evidence, 2),
        "recency":     round(recency, 2),
        "citation_v":  round(citation_v, 2),
        "composite":   final_score,  # Now stores the 10-point float
    }
    
    # Updated Output Payload
    paper["strategic_implication"] = " ".join(implications)
    paper["knowledge_graph_edge"]  = kg_edge
    paper["status"] = status
    paper["cross_disciplinary"] = cross_domains
    paper["days_old"] = days_old
    return paper


def score_and_rank(papers: list[dict], top_n: int = 15) -> list[dict]:
    scored = [compute_composite_score(p) for p in papers]
    scored.sort(key=lambda p: p["scores"]["composite"], reverse=True)

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

    needed = top_n - len(diverse_top)
    if needed > 0:
        diverse_top.extend(remainder[:needed])

    return diverse_top
