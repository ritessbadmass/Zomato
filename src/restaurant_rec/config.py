"""Load config.yaml + environment (RESTAURANT_REC_CONFIG, GROQ_API_KEY)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

_REPO_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_REPO_ROOT / ".env")


def _default_config_path() -> Path:
    override = os.environ.get("RESTAURANT_REC_CONFIG")
    if override:
        return Path(override)
    return _REPO_ROOT / "config.yaml"


@dataclass(frozen=True)
class AppConfig:
    repo_root: Path
    processed_catalog: Path
    dataset_hf_id: str
    dataset_split: str
    max_shortlist: int
    locality_top_n: int
    budget_low_max_inr: float
    budget_medium_max_inr: float
    relax_min_rating_delta: float
    groq_model: str
    groq_max_tokens: int
    groq_temperature: float
    groq_timeout: float
    prompt_version: str
    raw: dict[str, Any]


def load_config(path: Path | None = None) -> AppConfig:
    p = path or _default_config_path()
    with open(p, encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    paths = raw.get("paths", {})
    ds = raw.get("dataset", {})
    flt = raw.get("filter", {})
    gq = raw.get("groq", {})

    catalog = paths.get("processed_catalog", "data/processed/restaurants.parquet")
    processed = (_REPO_ROOT / catalog).resolve()

    return AppConfig(
        repo_root=_REPO_ROOT,
        processed_catalog=processed,
        dataset_hf_id=ds.get("hf_id", "ManikaSaini/zomato-restaurant-recommendation"),
        dataset_split=ds.get("split", "train"),
        max_shortlist=int(flt.get("max_shortlist_candidates", 40)),
        locality_top_n=int(flt.get("locality_top_n", 50)),
        budget_low_max_inr=float(flt.get("budget_low_max_inr", 300)),
        budget_medium_max_inr=float(flt.get("budget_medium_max_inr", 700)),
        relax_min_rating_delta=float(flt.get("relax_min_rating_delta", 0.5)),
        groq_model=gq.get("model", "llama-3.3-70b-versatile"),
        groq_max_tokens=int(gq.get("max_tokens", 2000)),
        groq_temperature=float(gq.get("temperature", 0.3)),
        groq_timeout=float(gq.get("timeout_seconds", 60)),
        prompt_version=str(raw.get("prompt_version", "v1")),
        raw=raw,
    )
