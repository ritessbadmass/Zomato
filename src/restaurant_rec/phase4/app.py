"""
FastAPI app: /api/v1/recommend, localities, locations, static web UI.
"""

from __future__ import annotations

import logging
import traceback
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from restaurant_rec.config import AppConfig, load_config
from restaurant_rec.phase1.ingest import run_ingest
from restaurant_rec.phase2.catalog_loader import load_catalog
from restaurant_rec.phase2.filter import filter_restaurants
from restaurant_rec.phase2.preferences import RecommendRequestBody, UserPreferences
from restaurant_rec.phase3.recommend import recommend

_REPO_ROOT = Path(__file__).resolve().parents[3]
_WEB_DIR = _REPO_ROOT / "web"
load_dotenv(_REPO_ROOT / ".env")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    cfg = load_config()
    if not cfg.processed_catalog.exists():
        logger.warning("Catalog missing at %s — running ingest", cfg.processed_catalog)
        run_ingest(cfg)
    n = len(load_catalog(cfg))
    print(f"Dataset loaded successfully. Total restaurants: {n}", flush=True)
    yield


app = FastAPI(title="Restaurant Rec", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok", "message": "Restaurant recommendation API running"}


@app.get("/api/v1/locations")
def api_locations():
    """Returns the broad 'city' zones available in the dataset (e.g. Whitefield, BTM)."""
    cfg = load_config()
    df = load_catalog(cfg)
    # The 'city' column in this dataset actually represents broad macro-zones in Bangalore.
    cities = sorted(df["city"].dropna().unique().tolist(), key=str.lower)
    return {"locations": cities}


@app.get("/api/v1/localities")
def api_localities(city: str | None = None):
    """Returns all distinct sub-localities for a given broad zone, excluding the zone name itself."""
    cfg = load_config()
    df = load_catalog(cfg)

    if city:
        # Filter down to the specific macro-zone (e.g. 'Banashankari')
        df = df[df["city"].str.lower() == city.lower()]
        # Return micro-localities within that zone, EXCLUDING the zone name itself
        # (since the city name always appears as one of its own localities in this dataset)
        all_locs = df["locality"].dropna().unique().tolist()
        sub_localities = [
            loc for loc in all_locs
            if loc.strip().lower() != city.strip().lower()
        ]
        localities = sorted(sub_localities, key=str.lower)
    else:
        # If no city is specified, return the top N localities overall
        top = (
            df["locality"]
            .value_counts()
            .head(cfg.locality_top_n)
            .index.tolist()
        )
        localities = sorted(top, key=str.lower)

    return {"localities": localities}


@app.post("/api/v1/recommend")
def api_recommend(body: RecommendRequestBody):
    cfg = load_config()
    try:
        prefs = body.preferences
        fr = filter_restaurants(prefs, cfg)
        shortlist = fr.shortlist

        if not shortlist:
            summary = (
                "No restaurants matched your filters."
                f" Reasons: {', '.join(fr.empty_reasons) or 'unknown'}."
            )
            return {
                "summary": summary,
                "items": [],
                "meta": {
                    "shortlist_size": 0,
                    "model": cfg.groq_model,
                    "prompt_version": cfg.prompt_version,
                    "duration_filter_ms": fr.duration_ms,
                    "duration_llm_ms": 0.0,
                    "relaxed_filters": fr.relaxed_steps,
                    "outcome": "empty",
                },
            }

        payload, llm_ms = recommend(prefs, shortlist, cfg)
        return {
            "summary": payload["summary"],
            "items": payload["items"],
            "meta": {
                "shortlist_size": len(shortlist),
                "model": cfg.groq_model,
                "prompt_version": cfg.prompt_version,
                "duration_filter_ms": fr.duration_ms,
                "duration_llm_ms": llm_ms,
                "relaxed_filters": fr.relaxed_steps,
                "outcome": "success",
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("recommend failed")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/")
def serve_index():
    idx = _WEB_DIR / "index.html"
    if not idx.exists():
        return JSONResponse(
            status_code=404,
            content={"detail": "Web UI not found. Add web/index.html."},
        )
    return FileResponse(str(idx))


if (_WEB_DIR / "static").is_dir():
    app.mount(
        "/static",
        StaticFiles(directory=str(_WEB_DIR / "static")),
        name="static",
    )
