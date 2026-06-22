<div align="center">
  <img src="https://raw.githubusercontent.com/Noetica-Intelligence/Noetica/main/docs/assets/noetica_logo.png" width="120" alt="Noetica Logo" />
  <h1>🌌 Noetica</h1>

  **Mapping the Evolution of Human Knowledge.**

  [![License: MIT](https://img.shields.io/badge/License-MIT-0f172a.svg?style=flat-square)](https://opensource.org/licenses/MIT)
  [![Zig Engine](https://img.shields.io/badge/Zig-0.16.0-F7A41D.svg?style=flat-square)](https://ziglang.org/)
  [![Python](https://img.shields.io/badge/Python-3.11-3776AB.svg?style=flat-square)](https://www.python.org/)
  [![Database](https://img.shields.io/badge/Database-PostgreSQL_|_SQLite-336791.svg?style=flat-square)]()
  [![Cloud](https://img.shields.io/badge/Cloud-Hugging_Face_|_GitHub_Pages-FFD21E.svg?style=flat-square)]()

  *Optimizing for Evidence, Scientific Significance, and Civilizational Importance.*

  **[🚀 VIEW THE LIVE 3D GALAXY DASHBOARD (GitHub Pages)](#)** 
</div>

---

## 📖 The Official Definition

**Noetica** is an open-source scientific intelligence network designed to discover, rank, connect, explain, and forecast the evolution of human knowledge across all disciplines.

Most systems optimize for attention, engagement, and trending topics. **Noetica optimizes for evidence.** We do not merely track papers. Noetica tracks discoveries, ideas, technologies, theories, knowledge networks, emerging disciplines, and civilization-scale transformations.

Single papers are noise. Trajectories are signal. Papers are leaves; the Discovery is the tree. Noetica maps the forest.

---

## 🧬 The 10 Non-Negotiable Principles

These principles override all feature decisions:

1. **Optimize for scientific significance**, not popularity.
2. **Social media is a sensor**, not a scoring factor.
3. **Discoveries are primary entities** — not papers.
4. **Knowledge graph** over flat category trees.
5. **Taxonomy must self-evolve** — not be hardcoded.
6. **Evidence beats attention** — always.
7. **Cross-disciplinary discoveries** receive higher priority.
8. **Open-source first**.
9. **Personalization without echo chambers** (the 80/20 forced exploration rule).
10. **Long-term civilizational impact** > short-term hype.

---

## 🏛️ V3 Dual-Engine Architecture

Noetica operates on an enterprise-grade hybrid-tier architecture combining the massive ecosystem of Python for data ingestion, the raw compiled speed of Zig for O(N²) Knowledge Graph calculations, and an autonomous LLM Agent for scientific synthesis.

```mermaid
graph TD
    A[Global Intel Sources] -->|arXiv, PubMed, Crunchbase, Patents| B(Python V3 Ingestion Engine)
    B -->|JSON Payload via stdin| C{Zig Native Engine}
    C -->|Math, Graph, Biosignals| D[(PostgreSQL / SQLite Dual-Engine)]
    D -->|Top Breakthroughs| E[LLM Polymath Agent]
    E -->|Synthesis & Digest| F[Resend / SendGrid Delivery]
```

### Core Layers
- **The Intelligence Fetchers:** Pulls real-time signals from arXiv, PubMed, ClinicalTrials, Semantic Scholar Conferences, NIH Grants, GitHub repos, and Crunchbase startup funding.
- **The Zig Core (`/zig_engine`):** A high-performance mathematics engine that calculates discovery significance, maps Jaccard semantic edges, and runs PageRank network centrality.
- **The Database Abstraction (`/src/database.py`):** Automatically scales from local SQLite to high-throughput PostgreSQL using dynamic schema mapping.
- **The Delivery Waterfall (`/src/send_email.py`):** Prioritizes HTTP API execution for enterprise ESPs (Resend, SendGrid) before falling back to legacy SMTP.

---

## 🌍 The Three Timelines of Knowledge

Noetica tracks discoveries across three parallel scopes:

| Timeline | Scope | Core Question | Example |
|----------|-------|---------------|---------|
| **Foundational** | 5,000+ years | What changed civilization? | *Calculus, Germ Theory, Transistors* |
| **Modern** | Last 50 years | What changed science? | *CRISPR-Cas9, AlphaFold, mRNA* |
| **Emerging** | Last 5 years | What might change the future? | *Quantum Error Correction, LLMs* |

Every node in the Noetica Knowledge Graph is tracked across its historical lifecycle:
`Speculative` ➔ `Emerging` ➔ `Growing` ➔ `Breakthrough` ➔ `Established` ➔ `Foundational` ➔ `Civilizational` ➔ `Historical`

---

## 🚀 Getting Started

### Prerequisites
* **Python 3.11+**
* **Zig 0.16.0**

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Noetica-Intelligence/Noetica.git
   cd Noetica
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment (Optional for V3 Enterprise Mode)**
   ```bash
   export DATABASE_URL="postgresql://user:pass@localhost:5432/noetica"
   export RESEND_API_KEY="re_123456789"
   export GEMINI_API_KEY="AI..."
   ```

4. **Run the Intelligence Pipeline**
   ```bash
   python src/main.py
   ```
   *To run a safe test trace without modifying production databases or dispatching emails, append `--dry-run`.*

---

<div align="center">
  <br>
  <i>Human understanding is the ultimate objective.</i>
</div>
