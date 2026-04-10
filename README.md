# Zomato AI (phase-wise architecture)

Restaurant recommendations: **Hugging Face catalog** → **deterministic filter** → **Groq LLM** for ranking and explanations. See `src/restaurant_rec/` for phases 1–4.

## Setup

1. Clone / open this repo.
2. Copy `.env.example` to `.env` and set **`GROQ_API_KEY`** ([Groq Console](https://console.groq.com/)).
3. Create a virtualenv (optional) and install the package in editable mode:

   ```bash
   pip install -e .
   ```

4. **Build the catalog** (Parquet under `data/processed/`):

   ```bash
   python scripts/ingest_zomato.py
   ```

   On first run the Hugging Face dataset download can take several minutes.

5. **Run the API + web UI**:

   ```bash
   uvicorn restaurant_rec.phase4.app:app --reload --host 127.0.0.1 --port 8000
   ```

6. Open **http://127.0.0.1:8000/** for the static UI, or **http://127.0.0.1:8000/docs** for OpenAPI.

### Configuration

- **`config.yaml`**: paths, filter caps (`max_shortlist_candidates`), budget tier INR cutoffs, Groq model name, `prompt_version`.
- **Environment**: `GROQ_API_KEY` (required for recommendations). Optional `RESTAURANT_REC_CONFIG` to point to an alternate YAML.

### API (summary)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/health` | Health check |
| GET | `/api/v1/locations` | Distinct cities |
| GET | `/api/v1/localities` | Top localities (for dropdown) |
| POST | `/api/v1/recommend` | Body: `{ "preferences": { "location", "budget_max_inr", "cuisine", "min_rating", "extras" } }` |

Response shape: `summary`, `items[]` (id, name, cuisines, rating, estimated_cost, cost_display, explanation, rank), `meta` (shortlist_size, model, prompt_version, timings, relaxed_filters).

### Canonical row (example)

After ingest, each Parquet row includes: `id`, `name`, `locality`, `city`, `cuisines`, `rating`, `cost_for_two`, `budget_tier`, `votes`, `address`, `has_online_order`, `has_table_booking`, `raw_features`.

### Notes

- If `data/processed/restaurants.parquet` is missing at startup, the app runs ingest automatically (same as the script).
- Do not commit `.env` or real API keys.
- Legacy flat `backend/` modules are deprecated; use `src/restaurant_rec/` (see `backend/README.md`).

### Optional: old Vite frontend

The `frontend/` folder may still exist from an earlier scaffold; the supported UI is **`web/`** served by FastAPI.
