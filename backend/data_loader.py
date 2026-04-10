"""
Zomato restaurant dataset: load, normalize, filter.
"""

from __future__ import annotations

import re
from typing import Any

import pandas as pd
from datasets import load_dataset

_DATAFRAME: pd.DataFrame | None = None


def _norm_col(name: str) -> str:
    return re.sub(r"\s+", " ", str(name).strip().lower())


def _norm_map(columns: list[str]) -> dict[str, str]:
    return {_norm_col(c): c for c in columns}


def _find_column(columns: list[str], patterns: list[str]) -> str | None:
    normalized = _norm_map(columns)
    for pat in patterns:
        p = pat.lower()
        for nc, orig in normalized.items():
            if p in nc or nc == p:
                return orig
    return None


def _map_columns(raw_df: pd.DataFrame) -> pd.DataFrame:
    raw_df = raw_df.copy()
    cols = list(raw_df.columns)
    by_norm = _norm_map(cols)
    mapping: dict[str, str] = {}

    name_col = (
        by_norm.get("name")
        or by_norm.get("restaurant name")
        or _find_column(
            cols,
            [
                "restaurant_name",
                "restaurant name",
                "restaurant",
                "restaurantname",
            ],
        )
    )
    loc_col = (
        by_norm.get("location")
        or by_norm.get("listed_in(city)")
        or by_norm.get("listed in (city)")
        or _find_column(
            cols,
            [
                "city",
                "area",
                "locality",
                "listed in",
                "listed_in",
            ],
        )
    )
    cuisine_col = by_norm.get("cuisines") or _find_column(
        cols,
        [
            "cuisine",
            "cuisine types",
        ],
    )
    cost_col = (
        by_norm.get("approx_cost(for two people)")
        or by_norm.get("avg_cost")
        or _find_column(
            cols,
            [
                "average cost",
                "avg_cost",
                "approx cost",
                "average cost for two",
                "cost",
            ],
        )
    )
    rating_col = (
        by_norm.get("rate")
        or by_norm.get("rating")
        or by_norm.get("aggregate rating")
        or _find_column(
            cols,
            [
                "aggregate rating",
                "aggregate_rating",
                "avg rating",
                "rating",
            ],
        )
    )
    votes_col = by_norm.get("votes") or _find_column(
        cols,
        [
            "number of votes",
            "vote",
            "reviews",
        ],
    )
    online_col = (
        by_norm.get("online_order")
        or by_norm.get("has_online_order")
        or _find_column(
            cols,
            [
                "online order",
                "online_order",
                "online ordering",
            ],
        )
    )
    booking_col = (
        by_norm.get("book_table")
        or by_norm.get("has_table_booking")
        or _find_column(
            cols,
            [
                "table booking",
                "book_table",
                "booking",
            ],
        )
    )

    if not name_col or not loc_col or not cuisine_col:
        raise ValueError(
            f"Could not map required columns. Got: {cols}. "
            f"Resolved name={name_col}, location={loc_col}, cuisines={cuisine_col}"
        )

    mapping["restaurant_name"] = name_col
    mapping["location"] = loc_col
    mapping["cuisines"] = cuisine_col
    if cost_col:
        mapping["avg_cost"] = cost_col
    else:
        raw_df = raw_df.copy()
        raw_df["_avg_cost_missing"] = 0.0
        mapping["avg_cost"] = "_avg_cost_missing"
    if rating_col:
        mapping["rating"] = rating_col
    else:
        raw_df["_rating_missing"] = 0.0
        mapping["rating"] = "_rating_missing"
    if votes_col:
        mapping["votes"] = votes_col
    else:
        raw_df["_votes_missing"] = 0
        mapping["votes"] = "_votes_missing"
    if online_col:
        mapping["has_online_order"] = online_col
    else:
        raw_df["_no_online"] = ""
        mapping["has_online_order"] = "_no_online"
    if booking_col:
        mapping["has_table_booking"] = booking_col
    else:
        raw_df["_no_booking"] = ""
        mapping["has_table_booking"] = "_no_booking"

    out = pd.DataFrame()
    for std, src in mapping.items():
        out[std] = raw_df[src]

    return out


def _to_boolish(val: Any) -> str:
    if pd.isna(val):
        return "no"
    s = str(val).strip().lower()
    if s in ("yes", "true", "1", "y"):
        return "yes"
    if s in ("no", "false", "0", "n"):
        return "no"
    return s if s else "no"


def _coerce_float(series: pd.Series) -> pd.Series:
    def one(x: Any) -> float:
        if pd.isna(x):
            return 0.0
        if isinstance(x, (int, float)):
            return float(x)
        s = str(x).strip()
        nums = re.findall(r"[-+]?\d*\.?\d+", s)
        if nums:
            try:
                return float(nums[0])
            except ValueError:
                return 0.0
        return 0.0

    return series.map(one)


def load_dataset_to_dataframe() -> pd.DataFrame:
    global _DATAFRAME
    if _DATAFRAME is not None:
        return _DATAFRAME

    ds = load_dataset("ManikaSaini/zomato-restaurant-recommendation", split="train")
    raw_df = ds.to_pandas()
    print("Dataset columns (raw):", list(raw_df.columns))

    df = _map_columns(raw_df)

    for c in ("restaurant_name", "location", "cuisines"):
        df[c] = df[c].astype(str).str.strip()
    df = df[
        (df["restaurant_name"].notna())
        & (df["restaurant_name"] != "")
        & (df["restaurant_name"].str.lower() != "nan")
        & (df["location"].notna())
        & (df["location"] != "")
        & (df["location"].str.lower() != "nan")
        & (df["cuisines"].notna())
        & (df["cuisines"] != "")
        & (df["cuisines"].str.lower() != "nan")
    ].copy()

    df["avg_cost"] = _coerce_float(df["avg_cost"])
    df["rating"] = _coerce_float(df["rating"])
    df["votes"] = _coerce_float(df["votes"])
    df.loc[df["avg_cost"].isna(), "avg_cost"] = 0.0
    df.loc[df["rating"].isna(), "rating"] = 0.0
    df.loc[df["votes"].isna(), "votes"] = 0.0

    for c in ("restaurant_name", "location", "cuisines"):
        df[c] = df[c].astype(str).str.strip()

    df["location"] = df["location"].str.title()
    df["cuisines"] = df["cuisines"].str.title()

    df["has_online_order"] = df["has_online_order"].map(_to_boolish)
    df["has_table_booking"] = df["has_table_booking"].map(_to_boolish)

    df["budget_band"] = df["avg_cost"].apply(_budget_band)

    _DATAFRAME = df
    return df


def _budget_band(avg_cost: float) -> str:
    if avg_cost <= 300:
        return "low"
    if avg_cost <= 700:
        return "medium"
    return "high"


def _apply_filters(
    df: pd.DataFrame,
    location: str,
    budget: str,
    cuisine: str,
    min_rating: float,
    use_cuisine: bool,
    use_budget: bool,
) -> pd.DataFrame:
    q = df.copy()
    loc_q = location.strip().lower()
    if loc_q:
        q = q[q["location"].str.lower().str.contains(loc_q, na=False, regex=False)]

    q = q[q["rating"] >= float(min_rating)]

    if use_budget and budget in ("low", "medium", "high"):
        q = q[q["budget_band"] == budget]

    if use_cuisine:
        c_q = cuisine.strip().lower()
        if c_q:
            q = q[q["cuisines"].str.lower().str.contains(c_q, na=False, regex=False)]

    q = q.sort_values(by=["rating", "votes"], ascending=[False, False])
    return q


def _row_to_dict(row: pd.Series) -> dict[str, Any]:
    return {
        "restaurant_name": str(row["restaurant_name"]),
        "location": str(row["location"]),
        "cuisines": str(row["cuisines"]),
        "avg_cost": float(row["avg_cost"]),
        "rating": float(row["rating"]),
        "votes": float(row["votes"]),
        "has_online_order": str(row["has_online_order"]),
        "has_table_booking": str(row["has_table_booking"]),
    }


def get_filtered_restaurants(
    location: str,
    budget: str,
    cuisine: str,
    min_rating: float,
    limit: int = 20,
) -> tuple[list[dict[str, Any]], bool]:
    df = load_dataset_to_dataframe()
    relaxed = False

    filtered = _apply_filters(
        df, location, budget, cuisine, min_rating, True, True
    )
    if len(filtered) == 0:
        filtered = _apply_filters(
            df, location, budget, cuisine, min_rating, False, True
        )
        if len(filtered) > 0:
            relaxed = True
    if len(filtered) == 0:
        filtered = _apply_filters(
            df, location, budget, cuisine, min_rating, False, False
        )
        if len(filtered) > 0:
            relaxed = True

    top = filtered.head(limit)
    out = [_row_to_dict(top.iloc[i]) for i in range(len(top))]
    return out, relaxed


def get_unique_values() -> dict[str, list[str]]:
    df = load_dataset_to_dataframe()
    loc_counts = df["location"].value_counts().head(50)
    locations = sorted(loc_counts.index.tolist(), key=str.lower)

    cuisine_parts: set[str] = set()
    for raw in df["cuisines"].dropna():
        for part in str(raw).split(","):
            p = part.strip()
            if p:
                cuisine_parts.add(p.title())
    cuisines = sorted(cuisine_parts, key=str.lower)

    return {"locations": locations, "cuisines": cuisines}


def preload_dataset() -> int:
    df = load_dataset_to_dataframe()
    return len(df)
