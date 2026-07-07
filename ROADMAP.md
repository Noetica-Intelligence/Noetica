# Noetica Roadmap

Noetica is an actively developed intelligence engine. This roadmap outlines the strategic direction for upcoming features and architectural scaling.

## Current (V1)
- [x] Python Orchestration & Pipeline Architecture
- [x] Zig Graph Scoring Engine (O(N²) Optimization)
- [x] LLM Synthesis via Gemini/Groq
- [x] Active Learning Loop (Community Feedback Injection)

## Upcoming (V2)
- `[x]` **Generalized 31x5 Web Dashboard**: A public-facing matrix tracking the absolute highest-signal discovery across all paradigms.
- `[ ]` **Local LLM Execution (Llama 3/Mistral)**: Removing the dependency on external APIs for highly-classified intelligence parsing.
- `[ ]` **Bi-directional Knowledge Graph Expansion**: Implementing a Neo4j or ArangoDB instance for persistent structural memory rather than in-memory matrix recalculations.
- `[ ]` **Customizable Signal Thresholds**: Allowing users to adjust the Noise-to-Signal ratio limits via a web interface.

## Future Vision (V3): The Polyglot Architecture

As Noetica scales to index the entirety of human scientific output in real-time, we will transition from a Python-centric orchestration model to a **high-performance, domain-optimized polyglot architecture**. Version 3 will leverage the absolute best-in-class languages for their respective architectural layers:

### 1. Rust (The Fetching Engine)
* **Goal**: Replace the Python I/O bounds with a blazingly fast, concurrent network fetcher.
* **Why Rust?**: Memory safety without garbage collection, combined with the `tokio` asynchronous runtime, will allow us to query thousands of scientific APIs (PubMed, arXiv, OpenAlex, GitHub, USPTO) concurrently in milliseconds rather than minutes.
* **Implementation Plan**: Port `v2_fetchers.py` into a compiled Rust microservice that streams deduplicated, sanitized JSON directly into the scoring pipeline.

### 2. R (Macro-Statistical Analysis)
* **Goal**: Understand the hidden trends of scientific velocity across all 31 paradigms.
* **Why R?**: R remains the undisputed leader in statistical modeling and data visualization. By tapping into Noetica's historical knowledge graph, R will calculate acceleration vs. deceleration trends, identify funding momentum, and map the trajectory of emerging fields.
* **Implementation Plan**: Integrate R scripts via the `rpy2` interface (or a dedicated REST API) to periodically ingest Noetica's database and output publication-grade predictive reports on paradigm shifts.

### 3. C++ (The Simulator & Heavy Integrator)
* **Goal**: Execute complex numerical integrations and molecular/physical simulations.
* **Why C++?**: While Zig handles our core O(N²) graph scoring engine, C++ (along with libraries like Eigen and Boost) is unparalleled for raw numerical simulation. As Noetica begins evaluating raw structural biology data or physics preprints, we will need high-performance compute to validate findings.
* **Implementation Plan**: Build out C++ worker nodes that can be invoked to run rapid simulations or molecular docking validations (e.g., verifying a newly ingested FGFR4 inhibitor discovery) before it hits the dashboard.

### 4. Zig (The Continuing Core)
* **Goal**: Maintain and expand the Zig Graph Scoring Engine.
* **Why Zig?**: Zig will remain the beating heart of Noetica, acting as the ultra-fast routing and scoring layer. The `score_graph` engine will be expanded to interface safely across C bindings with both the Rust fetchers and C++ simulation engines.

### 5. Meta-Analysis & Predictive Modeling
* **Automated Meta-Analysis**: Generating full, citation-backed literature reviews on-the-fly.
* **Predictive Breakthrough Modeling**: Using historical timeline data to predict fields on the verge of paradigm shifts before they enter the "Emerging" phase.
