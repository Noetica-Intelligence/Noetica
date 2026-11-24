import os
import sys
import json
import datetime
from unittest.mock import patch

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

import fetch_papers
import fetch_clinical_trials
import main as orchestrator


def test_fetch_clinical_trials_uses_timezone_utc_and_sets_source_types():
    sample_resp = json.dumps({
        "studies": [{
            "protocolSection": {
                "identificationModule": {"nctId": "NCT99999999", "briefTitle": "FGFR4 Inhibitor Trial"},
                "statusModule": {
                    "overallStatus": "RECRUITING",
                    "studyFirstPostDateStruct": {"date": "2026-11-20"},
                },
                "descriptionModule": {"briefSummary": "Phase 2 oncology trial."},
            }
        }]
    }).encode("utf-8")

    class FakeResp:
        def read(self):
            return sample_resp
        def __enter__(self):
            return self
        def __exit__(self, *args):
            return False

    with patch("urllib.request.urlopen", return_value=FakeResp()):
        trials = fetch_clinical_trials.fetch_recent_oncology_trials(days_back=7)

    assert len(trials) == 1
    assert trials[0]["id"] == "nct_NCT99999999"
    assert trials[0]["source_types"] == ["trial"]
    assert trials[0]["date"] == "2026-11-20"


def test_fetch_pubmed_uses_edat_and_slash_dates():
    captured_urls = []

    def fake_safe_get(url, timeout=20):
        captured_urls.append(url)
        if "esearch" in url:
            return json.dumps({"esearchresult": {"idlist": []}}).encode("utf-8")
        return b""

    with patch.object(fetch_papers, "safe_get", side_effect=fake_safe_get):
        fetch_papers.fetch_pubmed("circadian[Title/Abstract]", max_results=5)

    assert len(captured_urls) == 1
    url = captured_urls[0]
    assert "datetype=edat" in url
    assert "%2F" in url or "/" in url.split("mindate=")[1]


def test_fetch_openalex_filters_articles_with_abstracts():
    captured_urls = []

    def fake_safe_get(url, timeout=20):
        captured_urls.append(url)
        return json.dumps({"results": []}).encode("utf-8")

    with patch.object(fetch_papers, "safe_get", side_effect=fake_safe_get):
        fetch_papers.fetch_openalex("C86803240", max_results=4)

    assert len(captured_urls) == 1
    assert "type:article|preprint" in captured_urls[0]
    assert "has_abstract:true" in captured_urls[0]


def test_fetch_biorxiv_passes_category_slug():
    captured_urls = []

    def fake_safe_get(url, timeout=20):
        captured_urls.append(url)
        return json.dumps({"collection": []}).encode("utf-8")

    with patch.object(fetch_papers, "safe_get", side_effect=fake_safe_get):
        fetch_papers.fetch_biorxiv("cancer biology", max_results=5)

    assert len(captured_urls) == 1
    assert "?category=cancer_biology" in captured_urls[0]


def test_partition_matches_exact_domain_and_keywords():
    papers = [
        {"id": "1", "title": "Paper A", "abstract": "Unrelated abstract text", "domain": "Oncology", "source_types": ["paper"]},
        {"id": "2", "title": "Paper B", "abstract": "Pure string theory manifold", "domain": "Theoretical Physics", "source_types": ["paper"]},
        {"id": "3", "title": "Repo C", "abstract": "Oncology ML library", "domain": "Oncology", "source_types": ["repo"]},
    ]
    sub = {
        "Interests": "Oncology",
        "Discovery Preferences": "Research Papers",
        "Exploration Preference": "Yes",
    }
    matched, non_matching = orchestrator._partition_for_subscriber(papers, sub)
    assert [p["id"] for p in matched] == ["1"]
    assert [p["id"] for p in non_matching] == ["2"]
