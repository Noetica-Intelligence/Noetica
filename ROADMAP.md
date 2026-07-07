# Noetica Roadmap

Noetica is an actively developed intelligence engine. This roadmap outlines the strategic direction for upcoming features and architectural scaling.

## Current (V1)
- [x] Python Orchestration & Pipeline Architecture
- [x] Zig Graph Scoring Engine (O(N²) Optimization)
- [x] LLM Synthesis via Gemini/Groq
- [x] Active Learning Loop (Community Feedback Injection)

## Upcoming (V2)
- **Local LLM Execution (Llama 3/Mistral)**: Removing the dependency on external APIs for highly-classified intelligence parsing.
- **Bi-directional Knowledge Graph Expansion**: Implementing a Neo4j or ArangoDB instance for persistent structural memory rather than in-memory matrix recalculations.
- **Customizable Signal Thresholds**: Allowing users to adjust the Noise-to-Signal ratio limits via a web interface.

## Future Vision (V3): Polyglot Architecture
- **Rust (The Fetcher):** Replacing the Python fetching module with a highly concurrent Rust (`tokio`) service for blazing-fast, safe network I/O across thousands of APIs.
- **R (The Analyst):** Introducing R for macro-statistical analysis on the knowledge graph to identify acceleration and deceleration trends across the 31 paradigms.
- **C++ (The Simulator):** Implementing C++ for heavy numerical integrations and simulations, crucial for evaluating structural biology or physical discoveries if we outgrow the Zig engine.
- **Automated Meta-Analysis**: Generating full, citation-backed literature reviews on-the-fly.
- **Predictive Breakthrough Modeling**: Using historical timeline data to predict fields on the verge of paradigm shifts before they enter the "Emerging" phase.
