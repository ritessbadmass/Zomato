#!/usr/bin/env python3
"""One-command ingest: HF → data/processed/restaurants.parquet"""

from __future__ import annotations

import sys
from pathlib import Path

# allow `python scripts/ingest_zomato.py` from repo root without install
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_ROOT / "src"))

from restaurant_rec.config import load_config
from restaurant_rec.phase1.ingest import run_ingest


def main() -> None:
    cfg = load_config()
    run_ingest(cfg)


if __name__ == "__main__":
    main()
