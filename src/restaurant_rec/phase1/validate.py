"""Row-level validation; log drop reasons and counts."""

from __future__ import annotations

import logging
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)


def validate_catalog(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Drop invalid rows; return cleaned frame and stats dict."""

    n0 = len(df)
    stats: dict[str, Any] = {"rows_in": n0, "drops": {}}

    bad_name = df["name"].isna() | (df["name"].astype(str).str.strip() == "") | (
        df["name"].astype(str).str.lower() == "nan"
    )
    bad_loc = df["locality"].isna() | (df["locality"].astype(str).str.strip() == "") | (
        df["locality"].astype(str).str.lower() == "nan"
    )
    bad_cuisine = df["cuisines"].isna() | (df["cuisines"].astype(str).str.strip() == "") | (
        df["cuisines"].astype(str).str.lower() == "nan"
    )

    mask_drop = bad_name | bad_loc | bad_cuisine
    stats["drops"]["missing_name_location_or_cuisine"] = int(mask_drop.sum())

    df = df[~mask_drop].copy()

    df["rating"] = df["rating"].clip(lower=0.0, upper=5.0)

    stats["rows_out"] = len(df)
    stats["drops"]["total_dropped"] = n0 - len(df)
    logger.info(
        "Validation: in=%s out=%s drops=%s detail=%s",
        n0,
        stats["rows_out"],
        stats["drops"]["total_dropped"],
        stats["drops"],
    )
    return df, stats
