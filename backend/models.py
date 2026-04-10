from typing import Literal

from pydantic import BaseModel, Field


class UserPreferences(BaseModel):
    location: str
    budget: Literal["low", "medium", "high"]
    cuisine: str
    min_rating: float = Field(default=3.0, ge=0.0, le=5.0)
    extra_preferences: str = ""


class RecommendationRequest(BaseModel):
    preferences: UserPreferences
