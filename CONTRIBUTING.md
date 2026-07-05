# Contributing to Noetica

First off, thank you for considering contributing to Noetica! We welcome PRs from the community, especially regarding new data fetchers and improvements to the Zig scoring logic.

## Project Structure & The Triple-Engine Architecture

Noetica is not a standard monolithic application. It relies on a Triple-Engine design:
1. **Python Orchestrator (`src/main.py`)**: Handles async I/O, API fetching, and data wrangling.
2. **Zig Scoring Engine (`zig_engine/`)**: Handles the compute-heavy O(N²) graph mathematics (The NET Framework).
3. **LLM Synthesis**: Handled by Gemini/Groq via the orchestrator.

### The Active Learning Loop
If you are contributing to the Zig Scoring Engine, you must be aware of the Active Learning loop. Every 24 hours, `src/feedback.py` pulls user "Useful/Noise" feedback from Google Sheets and feeds it into the Zig engine. 
- **Positive Feedback** mathematically boosts adjacent graph nodes.
- **Negative Feedback** acts as a penalty weight.
Ensure that any new scoring heuristics respect this existing feedback injection.

## Development Workflow

We use a standard `Makefile` to simplify development.

### 1. Prerequisites
- Python 3.11+
- Zig 0.16.0+

### 2. Setup
```bash
# Clone the repository
git clone https://github.com/Noetica-Intelligence/Noetica.git
cd Noetica

# Install Python dependencies
make install

# Build the Zig scoring engine
make build-engine
```

### 3. Running the Pipeline
To run a full cycle of the orchestrator:
```bash
make run
```

## Pull Request Process
1. **Open an Issue First:** Before dedicating hours to a massive PR, please open an issue to discuss your proposed changes. This ensures alignment with the roadmap.
2. **Branch Naming:** Use `feature/<name>`, `bugfix/<name>`, or `chore/<name>`.
3. **Tests:** If you are adding a new fetcher, please add basic unit tests in `/tests/`.
4. **Code Style:** Python code should be typed and follow standard PEP8 conventions. Zig code should follow standard `zig fmt`.

We look forward to building the future of scientific intelligence with you.
