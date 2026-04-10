"""Map raw HF dataframe to canonical columns."""

from __future__ import annotations

import hashlib
import re
from typing import Any

import pandas as pd

_CITY_ALIASES = {
    "bengaluru": "Bangalore",
}


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


def _to_boolish(val: Any) -> str:
    if pd.isna(val):
        return "no"
    s = str(val).strip().lower()
    if s in ("yes", "true", "1", "y"):
        return "yes"
    if s in ("no", "false", "0", "n"):
        return "no"
    return s if s else "no"


def _budget_tier(cost: float, low_max: float, med_max: float) -> str:
    if cost <= 0:
        return "unknown"
    if cost <= low_max:
        return "low"
    if cost <= med_max:
        return "medium"
    return "high"


def _stable_id(name: str, locality: str, city: str) -> str:
    key = f"{name}|{locality}|{city}".encode("utf-8")
    return hashlib.sha256(key).hexdigest()[:24]


def map_raw_to_canonical(
    raw_df: pd.DataFrame,
    budget_low_max_inr: float = 300.0,
    budget_medium_max_inr: float = 700.0,
) -> pd.DataFrame:
    raw_df = raw_df.copy()
    cols = list(raw_df.columns)
    by_norm = _norm_map(cols)

    name_col = (
        by_norm.get("name")
        or by_norm.get("restaurant name")
        or _find_column(
            cols,
            ["restaurant_name", "restaurant name", "restaurant", "restaurantname"],
        )
    )
    locality_col = (
        by_norm.get("location")
        or _find_column(cols, ["locality", "area"])
    )
    city_col = by_norm.get("listed_in(city)") or by_norm.get("listed in (city)")
    cuisine_col = by_norm.get("cuisines") or _find_column(cols, ["cuisine", "cuisine types"])
    cost_col = (
        by_norm.get("approx_cost(for two people)")
        or by_norm.get("avg_cost")
        or _find_column(
            cols,
            ["average cost", "avg_cost", "approx cost", "average cost for two", "cost"],
        )
    )
    rating_col = (
        by_norm.get("rate")
        or by_norm.get("rating")
        or by_norm.get("aggregate rating")
        or _find_column(
            cols,
            ["aggregate rating", "aggregate_rating", "avg rating", "rating"],
        )
    )
    votes_col = by_norm.get("votes") or _find_column(
        cols, ["number of votes", "vote", "reviews"]
    )
    online_col = (
        by_norm.get("online_order")
        or by_norm.get("has_online_order")
        or _find_column(cols, ["online order", "online_order", "online ordering"])
    )
    booking_col = (
        by_norm.get("book_table")
        or by_norm.get("has_table_booking")
        or _find_column(cols, ["table booking", "book_table", "booking"])
    )
    address_col = by_norm.get("address")

    if not name_col or not locality_col or not cuisine_col:
        raise ValueError(
            f"Could not map required columns. Got: {cols}. "
            f"name={name_col}, locality={locality_col}, cuisines={cuisine_col}"
        )

    out = pd.DataFrame()
    out["name"] = raw_df[name_col].astype(str).str.strip()
    out["locality"] = raw_df[locality_col].astype(str).str.strip()
    if city_col:
        out["city"] = raw_df[city_col].astype(str).str.strip()
    else:
        out["city"] = out["locality"]

    for c in ("locality", "city"):
        out[c] = out[c].str.title()

    out["city"] = out["city"].map(
        lambda x: _CITY_ALIASES.get(str(x).strip().lower(), x)
    )

    out["cuisines"] = raw_df[cuisine_col].astype(str).str.strip().str.title()

    if cost_col:
        out["cost_for_two"] = _coerce_float(raw_df[cost_col])
    else:
        out["cost_for_two"] = 0.0

    if rating_col:
        out["rating"] = _coerce_float(raw_df[rating_col])
    else:
        out["rating"] = 0.0

    if votes_col:
        out["votes"] = _coerce_float(raw_df[votes_col])
    else:
        out["votes"] = 0.0

    out.loc[out["cost_for_two"].isna(), "cost_for_two"] = 0.0
    out.loc[out["rating"].isna(), "rating"] = 0.0
    out.loc[out["votes"].isna(), "votes"] = 0.0

    if online_col:
        out["has_online_order"] = raw_df[online_col].map(_to_boolish)
    else:
        out["has_online_order"] = "no"

    if booking_col:
        out["has_table_booking"] = raw_df[booking_col].map(_to_boolish)
    else:
        out["has_table_booking"] = "no"

    if address_col:
        out["address"] = raw_df[address_col].astype(str).str.strip()
    else:
        out["address"] = ""

    # Optional raw_features from text columns
    feat_parts = []
    if "dish_liked" in raw_df.columns:
        feat_parts.append(raw_df["dish_liked"].astype(str))
    else:
        feat_parts.append(pd.Series([""] * len(raw_df)))
    if "rest_type" in raw_df.columns:
        feat_parts.append(raw_df["rest_type"].astype(str))
    else:
        feat_parts.append(pd.Series([""] * len(raw_df)))
    out["raw_features"] = (
        feat_parts[0].str.slice(0, 200) + " | " + feat_parts[1].str.slice(0, 200)
    )

    out["budget_tier"] = out["cost_for_two"].apply(
        lambda c: _budget_tier(float(c), budget_low_max_inr, budget_medium_max_inr)
    )

    out["id"] = [
        _stable_id(
            str(out.iloc[i]["name"]),
            str(out.iloc[i]["locality"]),
            str(out.iloc[i]["city"]),
        )
        for i in range(len(out))
    ]

    # column order
    ordered = [
        "id",
        "name",
        "locality",
        "city",
        "cuisines",
        "rating",
        "cost_for_two",
        "budget_tier",
        "votes",
        "address",
        "has_online_order",
        "has_table_booking",
        "raw_features",
    ]
    return out[ordered]
