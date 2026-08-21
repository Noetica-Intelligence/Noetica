import sys
import os
import datetime
import pytest

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from score_papers import score_novelty, score_evidence, score_recency, score_domain_impact, get_cross_disciplinary_connections

def test_score_novelty():
    # Hype penalty
    score_hype = score_novelty("A groundbreaking AI breakthrough", "This is an unprecedented revolution.")
    assert score_hype <= 9.0, "Should penalize extreme hype words"
    
    # Genuine signals
    score_sig = score_novelty("First-principles proof", "Experimental observation confirms the manifold topology.")
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
