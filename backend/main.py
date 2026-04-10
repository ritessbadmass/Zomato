"""
FastAPI backend for Zomato AI restaurant recommendations.
"""

from __future__ import annotations

import logging
import traceback
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from data_loader import get_filtered_restaurants, get_unique_values, preload_dataset
from models import RecommendationRequest
from recommender import get_llm_recommendations

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    count = preload_dataset()
    print(
        f"Dataset loaded successfully. Total restaurants: {count}",
        flush=True,
    )
    yield


app = FastAPI(title="Zomato AI", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok", "message": "Zomato AI backend running"}


@app.get("/api/filters")
def filters():
    try:
        return get_unique_values()
    except Exception as e:
        logger.exception("filters failed")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load filters: {e!s}",
        ) from e


@app.post("/api/recommendations")
def recommendations(body: RecommendationRequest):
    try:
        prefs = body.preferences
        pdict = prefs.model_dump()

        filtered, relaxed = get_filtered_restaurants(
            location=prefs.location,
            budget=prefs.budget,
            cuisine=prefs.cuisine,
            min_rating=prefs.min_rating,
            limit=20,
        )

        if len(filtered) == 0:
            raise HTTPException(
                status_code=404,
                detail="No restaurants found. Try relaxing your filters.",
            )

        llm_result = get_llm_recommendations(pdict, filtered)

        out = dict(llm_result)
        out["total_filtered"] = len(filtered)
        out["relaxed_filters"] = relaxed
        return out
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("recommendations failed")
        tb = traceback.format_exc()
        logger.error(tb)
        raise HTTPException(
            status_code=500,
            detail=f"Recommendation error: {e!s}",
        ) from e
