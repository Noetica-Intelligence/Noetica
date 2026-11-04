import os
import sys
import tempfile
import pytest
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from bloom_dedup import BloomFilter, fingerprint, load_filter, save_filter, is_seen, mark_seen

def test_bloom_filter_basic():
    bf = BloomFilter(capacity=1000, error_rate=0.01)
    item = b"sample_paper_fingerprint_123"
    assert item not in bf
    bf.add(item)
    assert item in bf
    assert bf.count == 1

def test_bloom_filter_serialization():
    bf = BloomFilter(capacity=500, error_rate=0.005)
    bf.add(b"paper_a")
    bf.add(b"paper_b")
    
    data = bf.to_dict()
    assert "bits" in data
    assert data["count"] == 2
    
    bf2 = BloomFilter.from_dict(data)
    assert b"paper_a" in bf2
    assert b"paper_b" in bf2
    assert b"paper_c" not in bf2

def test_fingerprint_normalization():
    # Same paper with different casing, whitespace, and punctuation must yield identical fingerprint
    fp1 = fingerprint("Deep Learning for Drug Discovery: A Novel Approach", "We demonstrate state-of-the-art results.")
    fp2 = fingerprint("deep learning for drug discovery a novel approach", "we demonstrate state of the art results")
    assert fp1 == fp2

def test_load_save_filter(tmp_path, monkeypatch):
    monkeypatch.setattr("bloom_dedup.DEDUP_DIR", tmp_path)
    email = "researcher@example.com"
    
    bf = load_filter(email)
    assert bf.count == 0
    
    mark_seen(bf, "AlphaFold 3 Breakthrough", "Predicts biomolecular complex structures with accuracy.")
    assert is_seen(bf, "AlphaFold 3 Breakthrough", "Predicts biomolecular complex structures with accuracy.")
    assert not is_seen(bf, "Completely Different Paper", "Quantum algorithms for prime factorization.")
    
    save_filter(email, bf)
    
    # Reload from disk
    bf_reloaded = load_filter(email)
    assert bf_reloaded.count == 1
    assert is_seen(bf_reloaded, "AlphaFold 3 Breakthrough", "Predicts biomolecular complex structures with accuracy.")
