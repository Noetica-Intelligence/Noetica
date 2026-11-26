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
import source_registry
import subscribers
import v2_fetchers
import alerts
import ai_synthesis
import build_email
import send_email


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


def test_partition_matches_domain_aliases_without_semantic_model():
    papers = [
        {"id": "ai1", "title": "Scaling Transformers", "abstract": "Token routing study", "domain": "AI & Machine Learning", "source_types": ["paper"]},
        {"id": "med1", "title": "FGFR4 Inhibitor Study", "abstract": "Targeted liver therapy", "domain": "Oncology", "source_types": ["paper"]},
        {"id": "phys1", "title": "Dark Matter Halos", "abstract": "Galaxy formation simulation", "domain": "Astrophysics", "source_types": ["paper"]},
    ]
    sub = {
        "Interests": "Artificial Intelligence, Medicine",
        "Discovery Preferences": "Research Papers",
        "Exploration Preference": "Yes",
    }
    with patch.object(orchestrator, "semantic_model", None):
        matched, non_matching = orchestrator._partition_for_subscriber(papers, sub)
    assert [p["id"] for p in matched] == ["ai1", "med1"]
    assert [p["id"] for p in non_matching] == ["phys1"]


def test_sanitize_string_handles_none_and_dementia_grant_domain():
    assert v2_fetchers._sanitize_string(None) == ""
    grant = {
        "title": "[GRANT] Evaluating Care Pathways for People with Dementia",
        "abstract": "Medicare clinical study for aging patients.",
    }
    assert source_registry.infer_paradigm_domain(grant, default_domain="Medicine") == "Medicine"
    assert source_registry.assign_domain_from_chunk(grant, ["Mathematics", "Medicine"]) == "Medicine"


def test_parse_interests_parentheses_and_dataset_prefs():
    parsed = subscribers.parse_interests("Medicine (Oncology, Immunology), Artificial Intelligence")
    assert "Medicine" in parsed
    assert "Oncology" in parsed
    assert "Immunology" in parsed
    assert "Artificial Intelligence" in parsed

    types = subscribers.parse_discovery_preferences("Scientific Datasets / Technical Reports")
    assert "dataset" in types
    assert "repo" in types


def test_fetch_all_intelligence_tracks_raw_count_before_cap(monkeypatch):
    fake_items = [
        {
            "id": f"doc_{i}",
            "title": f"Distinct Scientific Discovery {i}",
            "abstract": f"Unique abstract body number {i} for clustering bypass.",
            "source": "arXiv",
            "source_types": ["paper"],
        }
        for i in range(12)
    ]
    fake_registry = [
        {
            "name": "arXiv",
            "type": "paper",
            "enabled": True,
            "fetcher": lambda: list(fake_items),
            "description": "Test source",
        }
    ]
    monkeypatch.setenv("MAX_PAPERS_TOTAL", "5")
    with patch.object(source_registry, "SOURCE_REGISTRY", fake_registry):
        result = source_registry.fetch_all_intelligence()
    assert len(result) == 5
    assert source_registry.fetch_all_intelligence.last_raw_count == 12


def test_dry_run_and_failed_send_preserve_bloom_filter(tmp_path, monkeypatch):
    fake_subs = [{
        "Email": "test@example.com",
        "Name": "Tester",
        "Reading Time": "10 Minutes",
        "Report Frequency": "Daily",
        "Interests": "Oncology",
        "Discovery Preferences": "Research Papers",
        "Exploration Preference": "No",
        "Expertise Level": "Advanced",
    }]
    fake_papers = [{
        "id": "p1",
        "title": "Novel FGFR4 Inhibition in Hepatocellular Carcinoma",
        "abstract": "Clinical trial shows n=120 efficacy p-value 0.01.",
        "domain": "Oncology",
        "source": "PubMed",
        "date": datetime.date.today().isoformat(),
        "url": "https://example.org/1",
        "authors": ["Smith A"],
        "source_types": ["paper"],
    }]
    monkeypatch.chdir(tmp_path)
    mark_calls = []
    save_calls = []

    with patch.object(orchestrator, "ingest_feedback_from_sheet", return_value=0), \
         patch.object(orchestrator, "get_subscribers", return_value=fake_subs), \
         patch.object(orchestrator, "fetch_all_intelligence", return_value=list(fake_papers)), \
         patch.object(orchestrator, "save_discoveries"), \
         patch.object(orchestrator, "check_and_fire_alerts", return_value=0), \
         patch.object(orchestrator, "get_emerging_trends", return_value=[]), \
         patch.object(orchestrator, "generate_personalized_synthesis", return_value=""), \
         patch.object(orchestrator, "format_abstract_pointwise", side_effect=lambda x: x), \
         patch.object(orchestrator, "mark_seen", side_effect=lambda *a: mark_calls.append(a)), \
         patch.object(orchestrator, "save_filter", side_effect=lambda *a: save_calls.append(a)), \
         patch.object(sys, "argv", ["main.py", "--dry-run"]):
        rc = orchestrator.main()

    assert rc == 0
    assert mark_calls == []
    assert save_calls == []

    # Failed SMTP send must also NOT persist Bloom filter
    with patch.object(orchestrator, "ingest_feedback_from_sheet", return_value=0), \
         patch.object(orchestrator, "get_subscribers", return_value=fake_subs), \
         patch.object(orchestrator, "fetch_all_intelligence", return_value=list(fake_papers)), \
         patch.object(orchestrator, "save_discoveries"), \
         patch.object(orchestrator, "check_and_fire_alerts", return_value=0), \
         patch.object(orchestrator, "get_emerging_trends", return_value=[]), \
         patch.object(orchestrator, "generate_personalized_synthesis", return_value=""), \
         patch.object(orchestrator, "format_abstract_pointwise", side_effect=lambda x: x), \
         patch.object(orchestrator, "send_digest", return_value=False), \
         patch.object(orchestrator, "mark_seen", side_effect=lambda *a: mark_calls.append(a)), \
         patch.object(orchestrator, "save_filter", side_effect=lambda *a: save_calls.append(a)), \
         patch.object(sys, "argv", ["main.py"]):
        rc2 = orchestrator.main()

    assert rc2 == 1
    assert mark_calls == []
    assert save_calls == []


def test_alerts_respect_dry_run_and_cap(monkeypatch):
    discoveries = [
        {
            "id": f"d_{i}",
            "title": "Breakthrough FGFR4 Circadian Therapy",
            "abstract": "Hepatocellular carcinoma chronotherapy study.",
            "scores": {"composite": 9.8},
            "cross_disciplinary": ["A", "B", "C"],
        }
        for i in range(10)
    ]
    subs = [{"Email": "user@example.com", "Discovery Preferences": "Emerging Frontiers"}]

    # dry_run must return 0 without calling SMTP or DB
    assert alerts.check_and_fire_alerts(discoveries, subs, dry_run=True) == 0

    monkeypatch.setenv("SENDER_EMAIL", "bot@example.com")
    monkeypatch.setenv("SENDER_PASSWORD", "secret")
    sent = []
    with patch.object(alerts, "_init_alert_table"), \
         patch.object(alerts, "_already_alerted", return_value=False), \
         patch.object(alerts, "_record_alert"), \
         patch.object(alerts, "_send_alert_email", side_effect=lambda *a: sent.append(a) or True):
        fired = alerts.check_and_fire_alerts(discoveries, subs, dry_run=False, max_alerts=3)
    assert fired == 3
    assert len(sent) == 3


def test_fetch_all_conferences_splits_issn_filters():
    called_venues = []

    def fake_fetch_conf(venue, max_results=4):
        called_venues.append(venue)
        return []

    with patch.object(source_registry, "fetch_conferences", side_effect=fake_fetch_conf), \
         patch.object(source_registry.time, "sleep"):
        source_registry._fetch_all_conferences()

    issn_calls = [v for v in called_venues if v.startswith("issn:")]
    assert len(issn_calls) >= 5
    assert all("|" not in v for v in issn_calls)


def test_paper_card_handles_empty_source_types_dict():
    html = build_email.paper_card(
        1,
        {
            "id": "empty_st_1",
            "title": "Circadian FGFR4 Study",
            "abstract": "Detailed mechanistic evidence.",
            "source": "Nature",
            "source_types": {},
            "domain": "Medicine",
            "url": "https://example.org/nature",
            "authors": ["Roy S"],
            "scores": {"composite": 8.7},
        },
        "sub@example.com",
    )
    assert "Circadian FGFR4 Study" in html
    assert "Nature" in html


def test_send_digest_uses_runtime_env_updates(monkeypatch):
    monkeypatch.setenv("SENDER_EMAIL", "bot@example.com")
    monkeypatch.setenv("RECIPIENT_EMAIL", "sub@example.com")
    monkeypatch.setenv("RESEND_API_KEY", "re_test_123")
    monkeypatch.delenv("SENDGRID_API_KEY", raising=False)
    monkeypatch.delenv("SENDER_PASSWORD", raising=False)

    captured = []
    with patch.object(
        send_email,
        "_send_via_resend",
        side_effect=lambda *a, **kw: captured.append((a, kw)) or True,
    ):
        ok = send_email.send_digest("Subject", "<p>Body</p>")

    assert ok is True
    assert len(captured) == 1
    assert captured[0][0][0] == "sub@example.com"
    assert captured[0][1]["sender_email"] == "bot@example.com"
    assert captured[0][1]["api_key"] == "re_test_123"


def test_alerts_fallback_to_resend_without_smtp_password(monkeypatch):
    monkeypatch.setenv("SENDER_EMAIL", "bot@example.com")
    monkeypatch.setenv("RESEND_API_KEY", "re_test_123")
    monkeypatch.delenv("SENDGRID_API_KEY", raising=False)
    monkeypatch.delenv("SENDER_PASSWORD", raising=False)
    monkeypatch.delenv("GMAIL_APP_PASSWORD", raising=False)

    discoveries = [{
        "id": "fgfr4_1",
        "title": "FGFR4 Inhibitor Chronotherapy Breakthrough",
        "abstract": "Hepatocellular carcinoma trial.",
        "scores": {"composite": 9.5},
        "cross_disciplinary": ["A", "B", "C"],
    }]
    subs = [{"Email": "user@example.com", "Discovery Preferences": "Emerging Frontiers"}]

    sent = []
    with patch.object(alerts, "_init_alert_table"), \
         patch.object(alerts, "_already_alerted", return_value=False), \
         patch.object(alerts, "_record_alert"), \
         patch.object(alerts, "_send_via_resend", side_effect=lambda *a, **kw: sent.append(a[0]) or True):
        fired = alerts.check_and_fire_alerts(discoveries, subs, dry_run=False, max_alerts=1)

    assert fired == 1
    assert sent == ["user@example.com"]


def test_paper_card_and_wildcard_render_structured_abstract_html():
    sample_structured = (
        "<b>1. Abstract Overview:</b><br>"
        "Proves leading coefficient formula with p < 0.05 and $IC_{50} < 10$. "
        "<script>bad()</script><br>"
        "<b>2. Research Details:</b><br>"
        " * <b>Topic:</b> Elliptic curves * <b>Workflow:</b> Proof construction<br>"
        "<b>3. Key Findings & Future Directions:</b><br>Significant advance."
    )
    wildcard_structured = (
        "<b>1. Abstract Overview:</b><br>Introduces QLAF.<br>"
        "<b>2. Research Details:</b><br>-<i>Topic: </i>Pretraining<br>-<i>Workflow: </i>3-seed"
    )
    main_paper = {
        "id": "math_1",
        "title": "Refined conjectures of Birch-Swinnerton-Dyer type",
        "abstract": "Fallback abstract",
        "structured_abstract": sample_structured,
        "source": "arXiv",
        "source_types": {"paper": 1},
        "domain": "Pure Mathematics",
        "url": "https://example.org/1",
        "authors": ["Castella F", "Sano T"],
        "scores": {"composite": 7.5},
    }
    wildcard_paper = {
        "id": "ai_1",
        "title": "Quantum H_{2}O & $E = mc^2$ Attention",
        "abstract": "Wildcard fallback",
        "structured_abstract": wildcard_structured,
        "source": "HuggingFace Datasets",
        "source_types": {"dataset": 1},
        "domain": "Engineering",
        "url": "https://example.org/2",
        "authors": ["IgnisCogitationis"],
        "scores": {"composite": 6.6},
    }

    html_doc = build_email.build_email_html(
        [main_paper, wildcard_paper],
        "2026-11-26",
        subscriber_email="sub@example.com",
        ai_synthesis_html="<p><b>Key theme:</b> Convergence at p < 0.01.</p>",
    )

    # AI HTML tags must render directly, never double-escaped as &lt;b&gt;
    assert "<b>1. Abstract Overview:</b>" in html_doc
    assert "<b>2. Research Details:</b>" in html_doc
    assert "<i>Topic: </i>" in html_doc
    assert "&lt;b&gt;" not in html_doc
    assert "&lt;br&gt;" not in html_doc
    assert "&lt;i&gt;" not in html_doc

    # Inline and hyphen-joined bullets are normalized cleanly
    assert "&bull; <b>Topic:</b>" in html_doc
    assert "&bull; <b>Workflow:</b>" in html_doc
    assert "&bull; <i>Topic: </i>" in html_doc
    assert "&bull; <i>Workflow: </i>" in html_doc

    # Unsafe tags and stray comparisons outside LaTeX are safely escaped, while LaTeX unescapes '<'
    assert "p &lt; 0.05" in html_doc
    assert "&lt;script&gt;bad()&lt;/script&gt;" in html_doc
    assert "<script>" not in html_doc
    assert "IC_%7B50%7D%20%3C%2010" in html_doc

    # Wildcard title LaTeX renders <sub> and <img> rather than escaping generated HTML
    assert "H<sub>2</sub>O" in html_doc
    assert "https://latex.codecogs.com/svg.image?E%20%3D%20mc%5E2" in html_doc
    assert "&lt;sub&gt;" not in html_doc
    assert "&lt;img" not in html_doc

    # AI synthesis safe markup renders and stray '<' is escaped
    assert "<p><b>Key theme:</b> Convergence at p &lt; 0.01.</p>" in html_doc


def test_clean_structured_html_preserves_bullets_and_strips_fences():
    raw = (
        "```html\n"
        "<b>1. Abstract Overview:</b><br>\n"
        "Summary text.\n"
        "<b>2. Research Details:</b><br>\n"
        "* **Topic:** FGFR4\n"
        "* **Workflow:** Docking\n"
        "**3. Key Findings:** Important.\n"
        "```"
    )
    cleaned = ai_synthesis._clean_structured_html(raw)
    assert not cleaned.startswith("```")
    assert not cleaned.endswith("```")
    assert "&bull; <b>Topic:</b>" in cleaned
    assert "&bull; <b>Workflow:</b>" in cleaned
    assert "<br><br><b>3. Key Findings:</b>" in cleaned


def test_paper_card_empty_structured_abstract_and_attr_sanitization():
    html_fallback = build_email.paper_card(
        1,
        {
            "id": "fb_1",
            "title": "Plain <Fallback> Paper",
            "abstract": "Raw abstract with p < 0.01 and <script>x</script>.",
            "structured_abstract": "",
            "source": "PubMed",
            "source_types": ["paper"],
            "domain": "Oncology",
            "url": "https://example.org/fb",
            "authors": ["Roy S"],
            "scores": {"composite": 8.0},
        },
        "sub@example.com",
    )
    assert "p &lt; 0.01" in html_fallback
    assert "&lt;script&gt;x&lt;/script&gt;" in html_fallback

    html_attr = build_email.paper_card(
        1,
        {
            "id": "attr_1",
            "title": "Attr Sanitization",
            "abstract": "Unused",
            "structured_abstract": '<b>Title</b> <b onclick="alert(1)">bad</b> <i>ok</i>',
            "source": "arXiv",
            "source_types": ["paper"],
            "domain": "Bioinformatics",
            "url": "https://example.org/attr",
            "authors": ["Roy S"],
            "scores": {"composite": 8.0},
        },
        "sub@example.com",
    )
    assert "<b>Title</b>" in html_attr
    assert "<i>ok</i>" in html_attr
    assert '&lt;b onclick="alert(1)"&gt;bad</b>' in html_attr
