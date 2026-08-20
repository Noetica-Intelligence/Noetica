# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Permanent Deduplication (Bloom Filters)**: Pure Python Bloom filter implementation ensuring papers are never sent twice to the same subscriber.
- **7 API Source Integration**: Fetchers added for arXiv, PubMed, bioRxiv, Semantic Scholar, OpenAlex, ClinicalTrials.gov, and GitHub Search.
- **Scoring Engine Balance**: Refined domain weights and hype penalties to balance Oncology, Biology, and AI paper scoring.
- **Web Dashboard Matrix**: Auto-generated 31x5 scientific paradigm matrix hosted on GitHub Pages.
- **Active Learning Loop**: Google Sheets integration for daily user feedback (Useful/Noise) to bias the Scoring Engine.
- **Triple-Engine Architecture**: Decoupled the orchestration (Python), scoring (Zig), and synthesis (LLM) layers.

### Removed
- Unused FastAPI backend directory.

## [1.0.0] - 2026-06-25
### Added
- Initial closed beta launch of the Noetica Engine.
- V1 Centrality Scoring logic.
- Gemini 1.5 Pro synthesis integration.
