"""
bloom_dedup.py -- Bloom Filter Deduplication Engine for Noetica
==============================================================

Architecture:
  * One Bloom filter per subscriber, stored in data/dedup/<email_hash>.bloom
  * Content-based fingerprinting: SHA-256(normalize(title + abstract))
    -> Same paper from arXiv AND PubMed AND Semantic Scholar = same fingerprint
    -> ID-based dedup CANNOT do this
  * Committed to Git after every run -> persists across ephemeral CI runners
  * Zero false negatives  (no repeated paper ever slips through)
  * ~0.1% false positive rate (1 in 1000 new papers wrongly skipped)
  * Fixed file size ~90 KB regardless of years of usage

Pure Python -- stdlib only (hashlib, math, struct, base64, re, json).
No pip install required.

Capacity sizing:
  10 papers/day x 365 days x 14 years = 51,100 papers -> capacity = 60,000
  At 0.1% error rate -> bit array ~86 KB per subscriber
"""

import math
import struct
import hashlib
import base64
import json
import re
from pathlib import Path

# ---------------------------------------------------------------------------
# Storage directory
# ---------------------------------------------------------------------------
DEDUP_DIR = Path("data") / "dedup"

# ---------------------------------------------------------------------------
# Bloom filter parameters
# Capacity: 60,000 items  (~14 years of 10-paper daily digests)
# Error rate: 0.1%  (1 false positive per 1,000 genuinely new discoveries)
# ---------------------------------------------------------------------------
_CAPACITY   = 60_000
_ERROR_RATE = 0.001


# ---------------------------------------------------------------------------
# Core Bloom Filter
# ---------------------------------------------------------------------------

def _optimal_params(capacity, error_rate):
    """Calculate optimal (m bits, k hash functions) for given capacity/error rate."""
    m = math.ceil(-capacity * math.log(error_rate) / (math.log(2) ** 2))
    k = round((m / capacity) * math.log(2))
    return m, k


def _hash_positions(item, m, k):
    """
    Double-hashing: h_i(x) = (h1(x) + i * h2(x)) % m
    Uses the first 16 bytes of SHA-256 split into two 64-bit ints.
    Produces k independent bit positions with a single hash call.
    """
    digest = hashlib.sha256(item).digest()
    h1 = struct.unpack_from("<Q", digest, 0)[0]
    h2 = struct.unpack_from("<Q", digest, 8)[0]
    if h2 == 0:
        h2 = 1
    return [(h1 + i * h2) % m for i in range(k)]


class BloomFilter:
    """
    A Bloom filter backed by a compact bytearray.

    Usage:
        bf = BloomFilter()
        bf.add(b"some bytes")
        b"some bytes" in bf  # -> True
    """

    def __init__(self, capacity=_CAPACITY, error_rate=_ERROR_RATE):
        self.capacity   = capacity
        self.error_rate = error_rate
        self.m, self.k  = _optimal_params(capacity, error_rate)
        self._bits      = bytearray(math.ceil(self.m / 8))
        self._count     = 0

    def _set_bit(self, pos):
        self._bits[pos >> 3] |= (1 << (pos & 7))

    def _get_bit(self, pos):
        return bool(self._bits[pos >> 3] & (1 << (pos & 7)))

    def add(self, item):
        """Add an item (bytes) to the filter."""
        for pos in _hash_positions(item, self.m, self.k):
            self._set_bit(pos)
        self._count += 1

    def __contains__(self, item):
        """Return True if item is probably in the set (no false negatives)."""
        return all(self._get_bit(pos) for pos in _hash_positions(item, self.m, self.k))

    @property
    def count(self):
        return self._count

    @property
    def fill_ratio(self):
        return sum(bin(b).count("1") for b in self._bits) / self.m

    def to_dict(self):
        return {
            "capacity":   self.capacity,
            "error_rate": self.error_rate,
            "m":          self.m,
            "k":          self.k,
            "count":      self._count,
            "bits":       base64.b64encode(self._bits).decode("ascii"),
        }

    @classmethod
    def from_dict(cls, data):
        bf = cls.__new__(cls)
        bf.capacity   = data["capacity"]
        bf.error_rate = data["error_rate"]
        bf.m          = data["m"]
        bf.k          = data["k"]
        bf._count     = data["count"]
        bf._bits      = bytearray(base64.b64decode(data["bits"]))
        return bf


# ---------------------------------------------------------------------------
# Content Fingerprinting
# ---------------------------------------------------------------------------

_STOPWORDS = frozenset({
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
    "being", "have", "has", "had", "do", "does", "did", "will", "would",
    "could", "should", "may", "might", "that", "this", "these", "those",
    "we", "our", "us", "it", "its", "as", "into", "than", "then", "also",
    "not", "no", "can", "which", "who", "whom", "what", "when", "where",
    "how", "all", "both", "each", "such", "more", "most", "other", "over",
    "under", "between", "through", "during", "before", "after", "above",
    "below", "up", "down", "out", "off", "about", "against", "across",
    "paper", "study", "results", "show", "using", "used", "based", "approach",
    "method", "methods", "model", "models", "data", "work", "new", "two",
    "within", "without", "while", "via", "however", "thus", "here",
})

_PUNCT_RE = re.compile(r"[^a-z0-9\s]")
_WS_RE    = re.compile(r"\s+")


def fingerprint(title, abstract):
    """
    Compute a content fingerprint for a discovery.

    Steps:
      1. Concatenate title + abstract
      2. Lowercase, strip punctuation
      3. Remove stopwords (domain-aware list above)
      4. SHA-256 -> full 32-byte digest

    Content-based: the same paper from arXiv, PubMed, and Semantic Scholar
    produces the identical fingerprint, catching cross-API duplicates that
    ID-based dedup cannot handle.
    """
    raw    = f"{title} {abstract}".lower()
    raw    = _PUNCT_RE.sub(" ", raw)
    tokens = [t for t in raw.split() if t not in _STOPWORDS and len(t) > 1]
    norm   = _WS_RE.sub(" ", " ".join(tokens)).strip()
    return hashlib.sha256(norm.encode("utf-8")).digest()


# ---------------------------------------------------------------------------
# Per-Subscriber Filter Storage
# ---------------------------------------------------------------------------

def _filter_path(email):
    """
    Return a stable, anonymized path for a subscriber's Bloom filter.
    Filename = first 16 hex chars of SHA-256(email) -> never exposes
    subscriber email addresses in the repo.
    """
    email_hash = hashlib.sha256(email.lower().strip().encode()).hexdigest()[:16]
    return DEDUP_DIR / f"{email_hash}.bloom"


def load_filter(email):
    """Load a subscriber's Bloom filter from disk, or create a fresh one."""
    path = _filter_path(email)
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return BloomFilter.from_dict(json.load(f))
        except Exception:
            pass  # corrupted -> fresh filter
    return BloomFilter()


def save_filter(email, bf):
    """Persist a subscriber's Bloom filter to disk."""
    DEDUP_DIR.mkdir(parents=True, exist_ok=True)
    path = _filter_path(email)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(bf.to_dict(), f, separators=(",", ":"))


# ---------------------------------------------------------------------------
# High-level helpers used by main.py
# ---------------------------------------------------------------------------

def is_seen(bf, title, abstract):
    """Return True if this discovery has probably been sent to this subscriber."""
    return fingerprint(title, abstract) in bf


def mark_seen(bf, title, abstract):
    """Record this discovery as seen in the subscriber's Bloom filter."""
    bf.add(fingerprint(title, abstract))
