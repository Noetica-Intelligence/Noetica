import os
import sys
import pytest

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from subscribers import parse_interests, parse_discovery_preferences, get_paper_limit_for_time

def test_parse_interests():
    assert parse_interests("AI, Oncology, Quantum Computing") == ["AI", "Oncology", "Quantum Computing"]
    assert parse_interests("All") == []
    assert parse_interests("") == []

def test_parse_discovery_preferences():
    prefs = "Research Papers, Patents, Open Source Projects, Clinical Trials"
    types = parse_discovery_preferences(prefs)
    assert "paper" in types
    assert "patent" in types
    assert "repo" in types
    assert "trial" in types

def test_get_paper_limit_for_time():
    assert get_paper_limit_for_time("5 Minutes") == 3
    assert get_paper_limit_for_time("10 Minutes") == 5
    assert get_paper_limit_for_time("15 Minutes") == 10
    assert get_paper_limit_for_time("30 Minutes") == 20
    assert get_paper_limit_for_time("Unknown") == 10
