"""Load processed Parquet into memory (startup)."""

from __future__ import annotations

import logging
from typing import Optional

import pandas as pd

from restaurant_rec.config import AppConfig, load_config

logger = logging.getLogger(__name__)

_CATALOG: Optional[pd.DataFrame] = None


def load_catalog(cfg: AppConfig | None = None) -> pd.DataFrame:
    """Read catalog from disk; cache at module level."""
    global _CATALOG
    cfg = cfg or load_config()
    path = cfg.processed_catalog
    if not path.exists():
        raise FileNotFoundError(
            f"Catalog not found at {path}. Run: python scripts/ingest_zomato.py"
        )
    df = pd.read_parquet(path)
    _CATALOG = df
    logger.info("Loaded catalog: %s rows from %s", len(df), path)
    return df


def get_catalog_df() -> pd.DataFrame:
    if _CATALOG is None:
        raise RuntimeError("Catalog not loaded; call load_catalog() first.")
    return _CATALOG
