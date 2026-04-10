"""Typed user preferences (API / domain)."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class UserPreferences(BaseModel):
    """Structured preferences aligned with POST /api/v1/recommend."""

    location: str = Field(
        ...,
        min_length=1,
        description="Matches catalog locality or city (substring).",
    )
    budget_max_inr: float = Field(
        ...,
        gt=0,
        le=200_000,
        description="Max approximate cost for two (INR).",
    )
    cuisine: str = Field(default="", description="Substring / token match on cuisines.")
    min_rating: float = Field(default=3.0, ge=0.0, le=5.0)
    extras: str = Field(default="", description="Free text for LLM / future boosts.")

    @field_validator("location", "cuisine", "extras", mode="before")
    @classmethod
    def strip_str(cls, v: object) -> object:
        if isinstance(v, str):
            return v.strip()
        return v


class RecommendRequestBody(BaseModel):
    preferences: UserPreferences
