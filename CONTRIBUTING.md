# Contributing to Noetica

First off, thank you for considering contributing to Noetica! It's people like you that make Noetica such a great tool.

## Getting Started

1. **Fork** the repository on GitHub.
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/your-username/scientific_intelligence.git
   ```
3. **Install** Python requirements:
   ```bash
   pip install -r requirements.txt
   ```

## Compiling the Zig Engine
Noetica uses a high-performance Graph Engine written in Zig to perform mathematical rankings and biosignal extraction on thousands of papers.

To run the engine locally, you **must** compile it first:
1. Install [Zig](https://ziglang.org/download/).
2. Navigate to the `zig_engine` directory.
3. Build the engine:
   ```bash
   cd zig_engine
   zig build -Doptimize=ReleaseFast
   ```
This will output the compiled binary to `zig_engine/zig-out/bin/zig_engine`. The Python orchestrator (`src/main.py`) expects the binary to be located here.

## Running the Engine
Set up your `.env` file using `.env.example` as a template.

To run the main intelligence pipeline:
```bash
python src/main.py
```

To run the FastAPI V2 Backend:
```bash
uvicorn backend.app.main:app --reload
```

## Pull Requests
- Please ensure all tests pass before submitting a PR.
- Document any new environment variables in `.env.example`.
