import sys
import os
import datetime
import pytest

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from score_papers import (
    score_novelty, score_evidence, score_recency, score_domain_impact,
    get_cross_disciplinary_connections, compute_composite_score, score_and_rank
)

def test_score_novelty():
    # Hype penalty
    score_hype = score_novelty("A groundbreaking AI breakthrough", "This is an unprecedented revolution.")
    assert score_hype <= 9.0, "Should penalize extreme hype words"
    
    # Genuine signals
    score_sig = score_novelty("First evidence of a new mechanism", "This discovery unifies the fields.")
    assert score_sig >= 8.0, "Should reward structural breakthrough keywords"

def test_score_evidence():
    score_high = score_evidence("We analyzed 5000 patients and n=400 control. p-value 0.05.")
    assert score_high > 5.0, "Should reward quantitative metrics"
    
def test_score_recency():
    today = datetime.date.today().isoformat()
    assert score_recency(today) == 10.0, "Today's papers should score 10.0"
    
    old_date = (datetime.date.today() - datetime.timedelta(days=10)).isoformat()
    assert score_recency(old_date) < 10.0, "Older papers should decay logarithmically"

def test_domain_impact():
    assert score_domain_impact("AI & Machine Learning") == 1.2
    assert score_domain_impact("Oncology") == 1.2
    assert score_domain_impact("Philosophy") == 1.0

def test_cross_disciplinary():
    connections = get_cross_disciplinary_connections("Quantum Computing")
    assert "Cryptography" in connections
    assert "AI" in connections

def test_compute_composite_score_sets_composite_score_key():
    paper = {
        "id": "test_paper_1",
        "title": "Novel mechanism of FGFR4 inhibition in hepatocellular carcinoma",
        "abstract": "We show in vivo clinical efficacy with n=450 patients. p-value 0.01.",
        "domain": "Oncology",
        "date": datetime.date.today().isoformat(),
        "source": "Nature",
        "cited_by": 5
    }
    scored = compute_composite_score(paper)
    assert "composite_score" in scored, "Must directly set 'composite_score' on paper dict"
    assert scored["composite_score"] > 0.0
    assert scored["scores"]["composite"] == scored["composite_score"]

def test_feedback_boost_applied():
    paper = {
        "id": "boost_paper_99",
        "title": "Quantum algorithms for molecular dynamics",
        "abstract": "Theorem and proof of linear speedup.",
        "domain": "Quantum Computing",
        "date": datetime.date.today().isoformat(),
        "source": "arXiv",
        "cited_by": 0
    }
    scored_unboosted = compute_composite_score(dict(paper), feedback_boosts={})
    scored_boosted = compute_composite_score(dict(paper), feedback_boosts={"boost_paper_99": 0.3})
    assert scored_boosted["composite_score"] >= scored_unboosted["composite_score"] + 0.25
