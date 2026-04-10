"""HF download → canonical DataFrame → Parquet."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import pandas as pd
from datasets import load_dataset

from restaurant_rec.config import AppConfig, load_config
from restaurant_rec.phase1.transform import map_raw_to_canonical
from restaurant_rec.phase1.validate import validate_catalog

logger = logging.getLogger(__name__)


def ingest_from_hf(cfg: AppConfig | None = None) -> tuple[pd.DataFrame, dict[str, Any]]:
    cfg = cfg or load_config()
    ds = load_dataset(cfg.dataset_hf_id, split=cfg.dataset_split)
    raw_df = ds.to_pandas()
    logger.info("HF columns (raw): %s", list(raw_df.columns))
    print("Dataset columns (raw):", list(raw_df.columns), flush=True)

    canon = map_raw_to_canonical(
        raw_df,
        budget_low_max_inr=cfg.budget_low_max_inr,
        budget_medium_max_inr=cfg.budget_medium_max_inr,
    )
    cleaned, vstats = validate_catalog(canon)
    meta = {"validation": vstats, "hf_columns": list(raw_df.columns)}
    return cleaned, meta


def write_catalog(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)
    logger.info("Wrote catalog: %s rows -> %s", len(df), path)


def run_ingest(cfg: AppConfig | None = None) -> Path:
    """Full ingest pipeline; returns path to written Parquet."""
    cfg = cfg or load_config()
    df, meta = ingest_from_hf(cfg)
    write_catalog(df, cfg.processed_catalog)
    print(
        f"Ingest complete. rows={len(df)} written to {cfg.processed_catalog}",
        flush=True,
    )
    print("Validation stats:", meta.get("validation", {}), flush=True)
    return cfg.processed_catalog
