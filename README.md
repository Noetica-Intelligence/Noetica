<div align="center">

<img src="assets/logo.png" width="300" alt="Noetica Logo" />

# Noetica
**Mapping the Evolution of Human Knowledge.**

[![License: MIT](https://img.shields.io/badge/License-MIT-0f172a.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Zig Engine](https://img.shields.io/badge/Zig-0.16.0-F7A41D.svg?style=for-the-badge&logo=zig&logoColor=white)](https://ziglang.org/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Database](https://img.shields.io/badge/Database-PostgreSQL_|_SQLite-336791.svg?style=for-the-badge&logo=postgresql&logoColor=white)]()

<br>

<i>Optimizing for Evidence, Scientific Significance, and Civilizational Importance.</i><br>
<b><a href="#">🚀 VIEW THE LIVE 3D GALAXY DASHBOARD</a></b>

<br>
</div>

<hr style="border: 1px solid #1e293b; margin: 40px 0;">

## 📖 The Official Definition

**Noetica** is an open-source scientific intelligence network designed to discover, rank, connect, explain, and forecast the evolution of human knowledge across all disciplines.

Most systems optimize for attention, engagement, and trending topics. **Noetica optimizes for evidence.** We do not merely track papers. Noetica tracks discoveries, ideas, technologies, theories, knowledge networks, emerging disciplines, and civilization-scale transformations.

> **Single papers are noise. Trajectories are signal.** Papers are leaves; the Discovery is the tree. Noetica maps the forest.

<br>

## 🧬 10 Non-Negotiable Principles

These principles serve as the constitution of the Noetica Engine. They override all feature decisions:

<table>
  <tr>
    <td width="50%">
      <b>1.</b> Optimize for <b>scientific significance</b>, not popularity.<br>
      <b>2.</b> Social media is a <b>sensor</b>, not a scoring factor.<br>
      <b>3.</b> <b>Discoveries</b> are primary entities — not papers.<br>
      <b>4.</b> <b>Knowledge graph</b> over flat category trees.<br>
      <b>5.</b> Taxonomy must <b>self-evolve</b> — not be hardcoded.
    </td>
    <td width="50%">
      <b>6.</b> <b>Evidence beats attention</b> — always.<br>
      <b>7.</b> <b>Cross-disciplinary discoveries</b> receive higher priority.<br>
      <b>8.</b> <b>Open-source first</b>.<br>
      <b>9.</b> Personalization <b>without echo chambers</b>.<br>
      <b>10.</b> <b>Long-term civilizational impact</b> > short-term hype.
    </td>
  </tr>
</table>

<br>

## 🏛️ V3 Dual-Engine Architecture

Noetica operates on an enterprise-grade hybrid-tier architecture combining the massive ecosystem of Python for data ingestion, the raw compiled speed of Zig for O(N²) Knowledge Graph calculations, and an autonomous LLM Agent for scientific synthesis.

```mermaid
graph TD
    %% Styling
    classDef default fill:#1e293b,stroke:#cbd5e1,stroke-width:2px,color:#f8fafc;
    classDef native fill:#0f172a,stroke:#F7A41D,stroke-width:3px,color:#f8fafc;
    classDef db fill:#0369a1,stroke:#bae6fd,stroke-width:2px,color:#ffffff;
    
    A[Global Intel Sources<br/>arXiv, PubMed, Patents] -->|JSON Payload via stdin| B
    B{Zig Native Engine<br/>Math, Graph, Biosignals}:::native -->|O N² Traversal| C
    C[(PostgreSQL / SQLite<br/>Dual-Engine)]:::db -->|Top Breakthroughs| D
    D[LLM Polymath Agent<br/>Synthesis & Digest] --> E[Resend / SendGrid Delivery]
```

### ⚙️ Core Layers
- **Intelligence Fetchers:** Pulls real-time signals from arXiv, PubMed, ClinicalTrials, Semantic Scholar Conferences, NIH Grants, GitHub repos, and Crunchbase startup funding.
- **The Zig Core (`/zig_engine`):** A high-performance mathematics engine that calculates discovery significance, maps Jaccard semantic edges, and runs PageRank network centrality.
- **The Database Abstraction (`/src/database.py`):** Automatically scales from local SQLite to high-throughput PostgreSQL using dynamic schema mapping.
- **The Delivery Waterfall (`/src/send_email.py`):** Prioritizes HTTP API execution for enterprise ESPs (Resend, SendGrid) before falling back to legacy SMTP.

<br>

## 🌍 The Three Timelines of Knowledge

Noetica tracks discoveries across three parallel scopes. Every node in the Knowledge Graph is tracked across a historical lifecycle: `Speculative` ➔ `Emerging` ➔ `Growing` ➔ `Breakthrough` ➔ `Established` ➔ `Foundational` ➔ `Civilizational` ➔ `Historical`.

| Timeline | Scope | Core Question | Real-World Example |
|:---------|:------|:--------------|:-------------------|
| **Foundational** | `5,000+ years` | *What changed civilization?* | Calculus, Germ Theory, Transistors |
| **Modern** | `Last 50 years` | *What changed science?* | CRISPR-Cas9, AlphaFold, mRNA |
| **Emerging** | `Last 5 years` | *What might change the future?* | Quantum Error Correction, LLMs |

<br>

## 🚀 Getting Started

<details>
<summary><b>Click here to view installation instructions</b></summary>
<br>

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

</details>

<br><br>

<div align="center">
  <i>Human understanding is the ultimate objective.</i>
</div>
