import os
import sys
import pytest

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from fetch_papers import cluster_discoveries

def test_cluster_discoveries_merges_source_types_and_preserves_pdf():
    paper1 = {
        "id": "arxiv_101",
        "title": "Quantum Error Correction via Surface Codes",
        "abstract": "We present an experimental implementation of surface codes with high fidelity.",
        "source": "arXiv",
        "source_types": ["paper"],
        "authors": ["Alice", "Bob"],
        "url": "https://arxiv.org/abs/101",
        "pdf_url": "https://arxiv.org/pdf/101.pdf",
        "cited_by": 2,
    }
    paper2 = {
        "id": "pat_999",
        "title": "Quantum Error Correction via Surface Codes",  # identical title
        "abstract": "We present an experimental implementation of surface codes with high fidelity.",
        "source": "Europe PMC",
        "source_types": ["patent"],
        "authors": ["Alice", "Charlie"],
        "url": "https://europepmc.org/article/PAT/999",
        "pdf_url": "",
        "cited_by": 10,
    }
    
    clusters = cluster_discoveries([paper1, paper2])
    assert len(clusters) == 1
    c = clusters[0]
    
    # source_types must have both "paper" and "patent"
    assert "paper" in c["source_types"]
    assert "patent" in c["source_types"]
    
    # Authors must be merged
    assert "Alice" in c["authors"]
    assert "Bob" in c["authors"]
    assert "Charlie" in c["authors"]
    
    # Highest cited_by should be retained
    assert c["cited_by"] == 10
    
    # pdf_url must be preserved
    assert c["pdf_url"] == "https://arxiv.org/pdf/101.pdf"
