.PHONY: install build-engine run test clean help

# Configuration
ZIG_BUILD_CMD := zig build -Doptimize=ReleaseFast
PYTHON := python
PIP := pip

help:
	@echo "Noetica Development Makefile"
	@echo "----------------------------"
	@echo "make install      - Install Python dependencies"
	@echo "make build-engine - Compile the Zig Scoring Engine"
	@echo "make run          - Run the Noetica Orchestrator (main.py)"
	@echo "make test         - Run test suite (pytest)"
	@echo "make clean        - Remove caches and build artifacts"

install:
	$(PIP) install -r requirements.txt

build-engine:
	cd zig_engine && $(ZIG_BUILD_CMD)

run:
	$(PYTHON) src/main.py

test:
	$(PYTHON) -m pytest tests/

clean:
	rm -rf __pycache__ .pytest_cache
	rm -rf zig_engine/zig-cache zig_engine/zig-out
