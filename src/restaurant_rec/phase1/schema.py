"""Canonical catalog schema (single source of truth after ingest)."""

from __future__ import annotations

from typing import TypedDict


class CanonicalRow(TypedDict, total=False):
    """Example JSON shape for one restaurant row (lists as JSON-serializable)."""

    id: str
    name: str
    locality: str
    city: str
    cuisines: str  # comma-separated in Parquet; parse to list in API
    rating: float
    cost_for_two: float
    budget_tier: str  # low | medium | high
    votes: float
    address: str
    has_online_order: str
    has_table_booking: str
    raw_features: str
