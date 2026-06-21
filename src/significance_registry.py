"""
Scientific Intelligence Engine — Scientific Significance Registry (C15)
A curated, versioned database of Foundational / Modern / Emerging discoveries
that provides historical context for every new paper or discovery.

Purpose:
  - Every new discovery is compared against this registry to assess
    relative historical significance.
  - The registry is the "historical context engine" — it shows where a
    new discovery sits in the chain of human knowledge.
  - It is intentionally hand-curated (not auto-generated) because the
    important decisions about what qualifies as "civilizational" should
    not be delegated to an algorithm.

Usage:
    from significance_registry import get_registry, find_related_foundations, get_trajectory

Structure of each entry:
    {
        "id":          str,   # unique slug
        "name":        str,   # discovery name
        "tier":        str,   # "Foundational" | "Modern" | "Emerging"
        "year":        str,   # year or range
        "domains":     list,  # fields this discovery belongs to
        "keywords":    list,  # for matching against new papers
        "trajectory":  list,  # what this builds upon (list of ids)
        "enables":     list,  # what this made possible (list of ids)
        "significance":float, # 0-10 (hand-scored)
        "summary":     str,
    }
"""

from typing import Optional

REGISTRY: list[dict] = [

    # ─────────────────────────────────────────────────────────────────────────
    # TIER: FOUNDATIONAL (5000 years)
    # ─────────────────────────────────────────────────────────────────────────

    {
        "id": "zero",
        "name": "Zero (as a number)",
        "tier": "Foundational",
        "year": "~628",
        "domains": ["Mathematics"],
        "keywords": ["zero", "number system", "positional notation", "brahmagupta"],
        "trajectory": [],
        "enables": ["calculus", "algebra", "computing"],
        "significance": 10.0,
        "summary": "Without zero: no algebra, no calculus, no computers, no AI.",
    },
    {
        "id": "calculus",
        "name": "Calculus",
        "tier": "Foundational",
        "year": "1665–1675",
        "domains": ["Mathematics", "Physics"],
        "keywords": ["calculus", "differential", "integral", "newton", "leibniz", "derivative"],
        "trajectory": ["zero", "algebra"],
        "enables": ["classical_mechanics", "electromagnetism", "machine_learning"],
        "significance": 10.0,
        "summary": "Made engineering, physics, and machine learning mathematically possible.",
    },
    {
        "id": "classical_mechanics",
        "name": "Classical Mechanics",
        "tier": "Foundational",
        "year": "1687",
        "domains": ["Physics"],
        "keywords": ["newton", "mechanics", "force", "motion", "gravity", "principia"],
        "trajectory": ["calculus"],
        "enables": ["electromagnetism", "thermodynamics", "aerospace"],
        "significance": 10.0,
        "summary": "First universal mathematical description of nature.",
    },
    {
        "id": "electromagnetism",
        "name": "Electromagnetism",
        "tier": "Foundational",
        "year": "1865",
        "domains": ["Physics", "Engineering"],
        "keywords": ["maxwell", "electromagnetic", "electric field", "magnetic field", "light wave"],
        "trajectory": ["classical_mechanics", "calculus"],
        "enables": ["radio", "internet", "computing", "photonics"],
        "significance": 10.0,
        "summary": "Created radio, internet, computers, and all telecommunications.",
    },
    {
        "id": "evolution",
        "name": "Evolution by Natural Selection",
        "tier": "Foundational",
        "year": "1859",
        "domains": ["Biology"],
        "keywords": ["darwin", "evolution", "natural selection", "species", "adaptation", "fitness"],
        "trajectory": [],
        "enables": ["genetics", "genomics", "ecology", "synthetic_biology"],
        "significance": 10.0,
        "summary": "Unified all of biology. Everything from genetics to medicine sits on this.",
    },
    {
        "id": "germ_theory",
        "name": "Germ Theory of Disease",
        "tier": "Foundational",
        "year": "1850s–1870s",
        "domains": ["Medicine", "Biology"],
        "keywords": ["pasteur", "koch", "germ", "bacteria", "microbe", "infection", "pathogen"],
        "trajectory": [],
        "enables": ["vaccination", "antibiotics", "modern_medicine"],
        "significance": 10.0,
        "summary": "Massively increased human life expectancy by identifying infectious causation.",
    },
    {
        "id": "relativity",
        "name": "Special and General Relativity",
        "tier": "Foundational",
        "year": "1905–1915",
        "domains": ["Physics"],
        "keywords": ["einstein", "relativity", "spacetime", "e=mc2", "gravity", "geodesic", "gps"],
        "trajectory": ["classical_mechanics", "electromagnetism"],
        "enables": ["cosmology", "gps", "gravitational_waves", "nuclear_energy"],
        "significance": 10.0,
        "summary": "GPS would fail without relativistic corrections. Changed time and space.",
    },
    {
        "id": "quantum_mechanics",
        "name": "Quantum Mechanics",
        "tier": "Foundational",
        "year": "1900–1930",
        "domains": ["Physics", "Chemistry"],
        "keywords": ["quantum", "planck", "bohr", "heisenberg", "schrödinger", "wave function", "superposition"],
        "trajectory": ["electromagnetism", "classical_mechanics"],
        "enables": ["transistor", "laser", "mri", "quantum_computing"],
        "significance": 10.0,
        "summary": "Semiconductors, lasers, MRI, quantum computing — all trace back here.",
    },
    {
        "id": "dna_structure",
        "name": "DNA Double Helix Structure",
        "tier": "Foundational",
        "year": "1953",
        "domains": ["Biology", "Biochemistry"],
        "keywords": ["dna", "watson", "crick", "franklin", "double helix", "nucleotide", "base pair"],
        "trajectory": ["evolution", "genetics"],
        "enables": ["molecular_biology", "genomics", "crispr", "pcr"],
        "significance": 10.0,
        "summary": "Started molecular biology. All genomic medicine traces back here.",
    },
    {
        "id": "turing_machine",
        "name": "Turing Machine & Computability",
        "tier": "Foundational",
        "year": "1936",
        "domains": ["Computer Science", "Mathematics"],
        "keywords": ["turing", "computability", "halting problem", "algorithm", "computation", "automaton"],
        "trajectory": ["calculus", "logic"],
        "enables": ["transistor", "internet", "machine_learning"],
        "significance": 10.0,
        "summary": "Theoretical basis of all modern computers.",
    },
    {
        "id": "transistor",
        "name": "Transistor",
        "tier": "Foundational",
        "year": "1947",
        "domains": ["Engineering", "Physics"],
        "keywords": ["transistor", "semiconductor", "bell labs", "shockley", "bardeen"],
        "trajectory": ["quantum_mechanics", "electromagnetism"],
        "enables": ["integrated_circuits", "internet", "computing", "smartphones"],
        "significance": 10.0,
        "summary": "Every computer chip depends on this. Enabled the digital age.",
    },
    {
        "id": "information_theory",
        "name": "Information Theory",
        "tier": "Foundational",
        "year": "1948",
        "domains": ["Mathematics", "Computer Science"],
        "keywords": ["shannon", "entropy", "bit", "channel capacity", "information theory", "compression"],
        "trajectory": ["turing_machine", "electromagnetism"],
        "enables": ["internet", "cryptography", "machine_learning", "data_compression"],
        "significance": 10.0,
        "summary": "Mathematical foundation of all digital communication.",
    },
    {
        "id": "vaccination",
        "name": "Vaccination",
        "tier": "Foundational",
        "year": "1796",
        "domains": ["Medicine", "Immunology"],
        "keywords": ["vaccine", "jenner", "smallpox", "immunity", "inoculation"],
        "trajectory": ["germ_theory"],
        "enables": ["modern_medicine", "mrna_vaccines", "immunotherapy"],
        "significance": 10.0,
        "summary": "Saved hundreds of millions of lives. Foundation of immunology.",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # TIER: MODERN (last 50 years)
    # ─────────────────────────────────────────────────────────────────────────

    {
        "id": "internet",
        "name": "The Internet",
        "tier": "Modern",
        "year": "1960s–1990s",
        "domains": ["Computer Science", "Engineering"],
        "keywords": ["internet", "ARPANET", "TCP/IP", "world wide web", "HTTP", "network"],
        "trajectory": ["transistor", "information_theory", "electromagnetism"],
        "enables": ["machine_learning", "llms", "e_commerce", "social_media"],
        "significance": 10.0,
        "summary": "Changed civilization. Everything digital depends on it.",
    },
    {
        "id": "pcr",
        "name": "Polymerase Chain Reaction (PCR)",
        "tier": "Modern",
        "year": "1983",
        "domains": ["Biology", "Biochemistry"],
        "keywords": ["PCR", "polymerase chain reaction", "mullis", "DNA amplification", "primer"],
        "trajectory": ["dna_structure"],
        "enables": ["genomics", "human_genome", "crispr", "covid_testing"],
        "significance": 9.5,
        "summary": "Ability to amplify DNA sequences — unlocked forensics, diagnostics, genomics.",
    },
    {
        "id": "human_genome",
        "name": "Human Genome Project",
        "tier": "Modern",
        "year": "1990–2003",
        "domains": ["Biology", "Bioinformatics", "Medicine"],
        "keywords": ["human genome", "genome sequencing", "HGP", "gene", "chromosome", "genomics"],
        "trajectory": ["dna_structure", "pcr"],
        "enables": ["bioinformatics", "crispr", "precision_medicine", "alphafold"],
        "significance": 9.5,
        "summary": "Foundation of modern genomics and precision medicine.",
    },
    {
        "id": "deep_learning",
        "name": "Deep Learning",
        "tier": "Modern",
        "year": "2006–2012",
        "domains": ["AI & Machine Learning", "Computer Science"],
        "keywords": ["deep learning", "neural network", "hinton", "lecun", "bengio", "backpropagation", "gpu training"],
        "trajectory": ["information_theory", "transistor"],
        "enables": ["llms", "alphafold", "computer_vision", "drug_discovery_ai"],
        "significance": 9.8,
        "summary": "Created the current AI era. Everything from LLMs to AlphaFold runs on this.",
    },
    {
        "id": "crispr",
        "name": "CRISPR-Cas9 Gene Editing",
        "tier": "Modern",
        "year": "2012",
        "domains": ["Biology", "Medicine", "Synthetic Biology"],
        "keywords": ["CRISPR", "Cas9", "gene editing", "doudna", "charpentier", "guide RNA", "genome editing"],
        "trajectory": ["human_genome", "pcr", "dna_structure"],
        "enables": ["gene_therapy", "synthetic_biology", "programmable_medicine"],
        "significance": 9.8,
        "summary": "Potentially as transformative as the transistor — makes genomes editable.",
    },
    {
        "id": "transformer",
        "name": "Transformer Architecture (Attention is All You Need)",
        "tier": "Modern",
        "year": "2017",
        "domains": ["AI & Machine Learning", "Computer Science"],
        "keywords": ["transformer", "attention mechanism", "self-attention", "vaswani", "BERT", "GPT"],
        "trajectory": ["deep_learning"],
        "enables": ["llms", "alphafold", "protein_language_models"],
        "significance": 9.7,
        "summary": "The architectural foundation of all modern large language models.",
    },
    {
        "id": "alphafold",
        "name": "AlphaFold — Protein Structure Prediction",
        "tier": "Modern",
        "year": "2021",
        "domains": ["Bioinformatics", "AI & Machine Learning", "Structural Biology"],
        "keywords": ["AlphaFold", "protein folding", "protein structure", "DeepMind", "pLDDT", "predicted structure"],
        "trajectory": ["deep_learning", "transformer", "human_genome"],
        "enables": ["drug_discovery_ai", "protein_language_models", "structural_biology_ai"],
        "significance": 9.5,
        "summary": "Solved protein folding. Biggest bioinformatics breakthrough of the decade.",
    },
    {
        "id": "mrna_vaccines",
        "name": "mRNA Vaccine Technology",
        "tier": "Modern",
        "year": "2020–2021",
        "domains": ["Medicine", "Immunology", "Biotechnology"],
        "keywords": ["mRNA vaccine", "BNT162b2", "lipid nanoparticle", "spike protein", "COVID", "Moderna", "Pfizer"],
        "trajectory": ["vaccination", "human_genome"],
        "enables": ["personalized_vaccines", "cancer_immunotherapy", "mrna_therapeutics"],
        "significance": 9.2,
        "summary": "Platform technology that may transform vaccine development permanently.",
    },
    {
        "id": "gravitational_waves",
        "name": "Gravitational Wave Detection (LIGO)",
        "tier": "Modern",
        "year": "2015",
        "domains": ["Physics", "Astrophysics"],
        "keywords": ["gravitational waves", "LIGO", "black hole merger", "interferometer", "GW150914"],
        "trajectory": ["relativity"],
        "enables": ["multi_messenger_astronomy", "black_hole_imaging"],
        "significance": 9.3,
        "summary": "Confirmed a century-old prediction. Opened gravitational wave astronomy.",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # TIER: EMERGING (last 5 years)
    # ─────────────────────────────────────────────────────────────────────────

    {
        "id": "llms",
        "name": "Large Language Models",
        "tier": "Emerging",
        "year": "2022+",
        "domains": ["AI & Machine Learning", "Computer Science"],
        "keywords": ["LLM", "GPT", "Claude", "Gemini", "large language model", "foundation model", "ChatGPT"],
        "trajectory": ["transformer", "deep_learning", "internet"],
        "enables": ["ai_scientists", "ai_drug_discovery", "code_generation", "reasoning_ai"],
        "significance": 9.9,   # TBD — historical importance still unfolding
        "summary": "Potentially the largest software paradigm shift since the internet.",
    },
    {
        "id": "protein_language_models",
        "name": "Protein Language Models (ESM, ProGen, etc.)",
        "tier": "Emerging",
        "year": "2021+",
        "domains": ["Bioinformatics", "AI & Machine Learning"],
        "keywords": ["protein language model", "ESM", "ProGen", "ProtGPT", "sequence generation", "protein design"],
        "trajectory": ["alphafold", "transformer"],
        "enables": ["de_novo_protein_design", "enzyme_engineering"],
        "significance": 8.8,
        "summary": "LLM technology applied to protein sequences — enables de novo protein design.",
    },
    {
        "id": "ai_drug_discovery",
        "name": "AI-Driven Drug Discovery",
        "tier": "Emerging",
        "year": "2020+",
        "domains": ["AI & Machine Learning", "Medicine", "Bioinformatics"],
        "keywords": ["AI drug discovery", "molecular generation", "GNN drug", "virtual screening AI", "ADMET prediction"],
        "trajectory": ["deep_learning", "alphafold", "human_genome"],
        "enables": ["personalized_medicine", "faster_clinical_trials"],
        "significance": 8.9,
        "summary": "Compresses drug discovery timelines from decades to years.",
    },
    {
        "id": "quantum_computing_nisq",
        "name": "NISQ-Era Quantum Computing",
        "tier": "Emerging",
        "year": "2019+",
        "domains": ["Physics", "Computer Science", "Engineering"],
        "keywords": ["quantum computing", "qubit", "NISQ", "quantum advantage", "error correction", "superconducting"],
        "trajectory": ["quantum_mechanics", "transistor", "information_theory"],
        "enables": ["quantum_cryptography", "quantum_simulation", "optimization"],
        "significance": 8.5,
        "summary": "Still early, but transformative potential in cryptography, drug discovery, optimization.",
    },
    {
        "id": "ai_scientists",
        "name": "AI Scientists / Autonomous Research Agents",
        "tier": "Emerging",
        "year": "2024+",
        "domains": ["AI & Machine Learning", "Science"],
        "keywords": ["AI scientist", "autonomous research", "hypothesis generation", "AI agent science"],
        "trajectory": ["llms", "alphafold"],
        "enables": ["accelerated_discovery", "self_driving_labs"],
        "significance": 8.7,
        "summary": "AI systems that generate, test, and refine scientific hypotheses autonomously.",
    },
    {
        "id": "chronotherapy",
        "name": "Chronotherapy & Circadian Pharmacology",
        "tier": "Emerging",
        "year": "2018+",
        "domains": ["Medicine", "Circadian Biology", "Oncology"],
        "keywords": ["chronotherapy", "circadian", "CLOCK", "BMAL1", "drug timing", "chronopharmacology"],
        "trajectory": ["vaccination", "human_genome"],
        "enables": ["precision_dosing", "chrono_oncology"],
        "significance": 8.0,
        "summary": "Drug timing affects efficacy and side effects — especially in oncology.",
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# LOOKUP FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def get_registry() -> list[dict]:
    """Return the full registry."""
    return REGISTRY


def get_by_tier(tier: str) -> list[dict]:
    """Get all entries in a given tier: Foundational | Modern | Emerging"""
    return [r for r in REGISTRY if r["tier"] == tier]


def find_related_foundations(paper: dict) -> list[dict]:
    """
    Given a new paper dict (with title + abstract + domain),
    return matching registry entries whose keywords appear in the paper text.
    Scored by number of keyword hits.
    """
    text = ((paper.get("title") or "") + " " + (paper.get("abstract") or "")).lower()
    scored: list[tuple[int, dict]] = []

    for entry in REGISTRY:
        hits = sum(1 for kw in entry["keywords"] if kw.lower() in text)
        if hits > 0:
            scored.append((hits, entry))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [entry for _, entry in scored[:5]]


def get_trajectory(discovery_id: str) -> list[dict]:
    """
    Return the full knowledge trajectory leading to a discovery.
    Example: get_trajectory("llms") →
      [information_theory, transistor, deep_learning, transformer, llms]
    """
    index = {r["id"]: r for r in REGISTRY}
    result = []
    visited = set()

    def walk(did: str, depth: int = 0):
        if did in visited or depth > 10:
            return
        visited.add(did)
        entry = index.get(did)
        if not entry:
            return
        for parent_id in entry.get("trajectory", []):
            walk(parent_id, depth + 1)
        result.append(entry)

    walk(discovery_id)
    return result


def score_against_registry(paper: dict) -> float:
    """
    Return a 0-1.5 bonus multiplier based on how close a new paper is
    to foundational/modern discoveries in the registry.
    Foundational match = bigger bonus.
    """
    related = find_related_foundations(paper)
    if not related:
        return 1.0

    tier_bonus = {"Foundational": 0.3, "Modern": 0.2, "Emerging": 0.1}
    bonus = sum(tier_bonus.get(r["tier"], 0) for r in related[:3])
    return round(min(1.0 + bonus, 1.5), 3)


if __name__ == "__main__":
    print(f"Registry loaded: {len(REGISTRY)} entries")
    for tier in ["Foundational", "Modern", "Emerging"]:
        entries = get_by_tier(tier)
        print(f"\n{tier} ({len(entries)}):")
        for e in entries:
            print(f"  [{e['significance']:.1f}] {e['name']} ({e['year']})")
