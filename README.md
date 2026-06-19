<div align="center">
  
# 🌌 Noetica

**Mapping the Evolution of Human Knowledge.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Zig](https://img.shields.io/badge/Zig-0.16.0-orange.svg)](https://ziglang.org/)
[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Database](https://img.shields.io/badge/Database-SQLite%20%7C%20PostgreSQL-336791.svg)]()

*Noetica optimizes for Evidence, Scientific Significance, and Civilizational Importance.*

</div>

---

## 📖 Official Definition

Noetica is an open-source scientific intelligence network designed to discover, rank, connect, explain, and forecast the evolution of human knowledge across all disciplines. 

Most systems optimize for attention, engagement, and trending topics. **Noetica optimizes for evidence.** We do not merely track papers. Noetica tracks discoveries, ideas, technologies, theories, knowledge networks, emerging disciplines, and civilization-scale transformations.

### 🧬 Non-Negotiable Principles
1. **Rank discoveries, not papers.**
2. **Evidence over popularity.**
3. **Social media weight = 0%.**
4. **Knowledge is a graph, not a folder structure.**
5. **Forecast with probabilities, never certainty.**

---

## 🏗️ Architecture (V3)

Noetica operates on a hybrid-tier architecture combining the massive ecosystem of Python for data ingestion with the raw, compiled speed of Zig for O(N²) Knowledge Graph calculations.

```mermaid
graph TD
    A[Global Intel Sources] -->|arXiv, PubMed, OpenAlex| B(Python Ingestion Engine)
    B -->|Patents, Grants, GitHub| B
    B -->|@embedFile JSON| C{Zig Native Engine}
    C -->|O N² Traversal| D[Graph Nodes & Edges]
    C -->|Civilizational Forecasting| D
    D -->|SQLAlchemy| E[(PostgreSQL / SQLite)]
    E --> F[V2 Dashboard UI]
    E --> G[Automated Daily Email Service]
```

### Components
- **The Ingestion Layer:** Pulls real-time data from global scientific APIs, patent databases, and NIH grants.
- **The Zig Core (`/zig_engine`):** A high-performance computation engine that calculates discovery significance, maps cross-disciplinary edges, and assigns **Civilizational Impact Forecast** probabilities.
- **The Graph Database (`/backend`):** A relational representation of the Knowledge Graph storing Nodes and Edges.
- **The Intelligence Reporter (`/src`):** Automatically dispatches an HTML intelligence briefing via Gmail SMTP.

---

## 🚀 Getting Started

### Prerequisites
* **Python 3.11+**
* **Zig 0.16.0**

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Noetica-Intelligence/core.git
   cd core
   ```

2. **Install Python dependencies**
   ```bash
   pip install requests beautifulsoup4 sqlalchemy
   ```

3. **Run the V3 Knowledge Graph Pipeline**
   This script fetches global data, compiles the Zig engine dynamically, calculates the graph, and stores it in the local SQLite database.
   ```bash
   python backend/ingest_v3.py
   ```

4. **Send a Dry-Run Intelligence Report**
   To generate a local `latest_report.html` without sending an email:
   ```bash
   python src/send_daily_report.py
   ```

---

## 📧 Automated Cloud Deployment

Noetica is designed to run completely autonomously at `$0/month` using GitHub Actions and Gmail SMTP.

1. Create a dedicated Gmail account (e.g., `noetica.intelligence@gmail.com`).
2. Generate an **App Password** in Google Security Settings.
3. Add the following **Repository Secrets** in GitHub:
   - `NOETICA_EMAIL`
   - `NOETICA_APP_PASSWORD`
   - `NOETICA_SUBSCRIBERS` (Comma-separated list of emails to receive the report)
4. The GitHub Action will run automatically every day at 8:00 AM UTC.

---

## 🌍 The Discovery Lifecycle

Every node in the Noetica Knowledge Graph is tracked across its historical lifecycle:
`Speculative` ➔ `Emerging` ➔ `Growing` ➔ `Breakthrough` ➔ `Established` ➔ `Foundational` ➔ `Civilizational` ➔ `Historical`

---

<div align="center">
  <i>Human understanding is the ultimate objective.</i>
</div>
