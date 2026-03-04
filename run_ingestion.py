"""
Root-level entry point for the FPL data ingestion pipeline.
Run this from the repo root: python run_ingestion.py
GitHub Actions also calls this directly, avoiding any sys.path / PYTHONPATH issues.
"""
import sys
import os

# Ensure the repo root is always on sys.path regardless of how this is invoked
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.ingestion.runner import main  # noqa: E402

if __name__ == "__main__":
    main()
