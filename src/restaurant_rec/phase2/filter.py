"""Deterministic shortlist from catalog + preferences."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pandas as pd

from restaurant_rec.config import AppConfig, load_config
from restaurant_rec.phase2.catalog_loader import get_catalog_df
from restaurant_rec.phase2.preferences import UserPreferences


@dataclass
class FilterResult:
    shortlist: list[dict[str, Any]]
    relaxed_steps: list[str] = field(default_factory=list)
    empty_reasons: list[str] = field(default_factory=list)
    duration_ms: float = 0.0


def _match_location(df: pd.DataFrame, q: str) -> pd.Series:
    q = q.strip().lower()
    if not q:
        return pd.Series(True, index=df.index)
    loc = df["locality"].astype(str).str.lower()
    city = df["city"].astype(str).str.lower()
    return loc.str.contains(q, na=False, regex=False) | city.str.contains(
        q, na=False, regex=False
    )


def _match_cuisine(df: pd.DataFrame, q: str) -> pd.Series:
    q = q.strip().lower()
    if not q:
        return pd.Series(True, index=df.index)
    return df["cuisines"].astype(str).str.lower().str.contains(
        q, na=False, regex=False
    )


def _match_budget(df: pd.DataFrame, budget_max_inr: float) -> pd.Series:
    """Known cost must be <= max; unknown (0) passes."""

    cost = df["cost_for_two"].astype(float)
    known = cost > 0
    ok_known = ~known | (cost <= float(budget_max_inr))
    return ok_known


def _apply(
    df: pd.DataFrame,
    prefs: UserPreferences,
    *,
    use_cuisine: bool,
    use_budget: bool,
    min_rating: float,
) -> pd.DataFrame:
    q = df.loc[_match_location(df, prefs.location)]
    q = q[q["rating"] >= min_rating]
    if use_budget:
        q = q.loc[_match_budget(q, prefs.budget_max_inr)]
    if use_cuisine:
        q = q.loc[_match_cuisine(q, prefs.cuisine)]
    q = q.sort_values(by=["rating", "votes"], ascending=[False, False])
    return q


def filter_restaurants(
    prefs: UserPreferences,
    cfg: AppConfig | None = None,
) -> FilterResult:
    import time

    t0 = time.perf_counter()
    cfg = cfg or load_config()
    df = get_catalog_df()
    relaxed: list[str] = []

    min_r = float(prefs.min_rating)

    def take(head: pd.DataFrame) -> list[dict[str, Any]]:
        cap = cfg.max_shortlist
        # Deduplicate by name to ensure a diverse shortlist
        # We lowercase the name temporarily to catch slight casing differences
        # But we can just use the exact name for simplicity
        if not head.empty and "name" in head.columns:
            head_dedup = head.drop_duplicates(subset=["name"])
        else:
            head_dedup = head
        rows = head_dedup.head(cap)
        return rows.to_dict(orient="records")

    # 1) full
    cur = _apply(df, prefs, use_cuisine=True, use_budget=True, min_rating=min_r)
    if len(cur) == 0:
        cur = _apply(df, prefs, use_cuisine=False, use_budget=True, min_rating=min_r)
        if len(cur) > 0:
            relaxed.append("cuisine")

    if len(cur) == 0:
        cur = _apply(df, prefs, use_cuisine=False, use_budget=False, min_rating=min_r)
        if len(cur) > 0:
            relaxed.append("budget_max_inr")

    if len(cur) == 0:
        min_r2 = max(0.0, min_r - cfg.relax_min_rating_delta)
        cur = _apply(
            df, prefs, use_cuisine=False, use_budget=False, min_rating=min_r2
        )
        if len(cur) > 0:
            relaxed.append(f"min_rating->{min_r2}")

    if len(cur) == 0:
        if _match_location(df, prefs.location).sum() == 0:
            reasons = ["NO_LOCATION"]
        else:
            reasons = ["NO_MATCH"]
        return FilterResult(
            shortlist=[],
            relaxed_steps=relaxed,
            empty_reasons=reasons,
            duration_ms=(time.perf_counter() - t0) * 1000,
        )

    out = take(cur)
    return FilterResult(
        shortlist=out,
        relaxed_steps=relaxed,
        empty_reasons=[],
        duration_ms=(time.perf_counter() - t0) * 1000,
    )
