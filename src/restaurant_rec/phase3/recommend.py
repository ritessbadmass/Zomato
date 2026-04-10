"""Orchestrate: shortlist → Groq → merge with catalog facts."""

from __future__ import annotations

import json
import logging
import re
import time
from typing import Any

from restaurant_rec.config import AppConfig, load_config
from restaurant_rec.phase2.preferences import UserPreferences
from restaurant_rec.phase3.groq_client import chat_completion

logger = logging.getLogger(__name__)

SYSTEM = """You are an expert restaurant recommender for India (Zomato-style data).
Rules:
- You MUST only recommend restaurants whose id appears in the provided shortlist JSON.
- Never invent restaurants or numeric facts; use only ids from the list.
- Respect the user's max budget (cost for two in INR) and minimum rating when choosing order.
- **Dietary Needs**: Pay extreme attention to tags like 'Vegetarian' or 'Non-Vegetarian'.
    - If the user specifies 'Vegetarian', avoid restaurants primarily known for meat or seafood unless they have a strong veg reputation.
    - If the user specifies 'Non-Vegetarian', prioritize places famous for their non-veg specialties (kebabs, biryani, etc.).
- Infer suitability from the restaurant name, cuisines, and locality if not explicitly labeled.
- Output valid JSON only, no markdown fences."""


def _build_user_prompt(
    prefs: UserPreferences,
    shortlist: list[dict[str, Any]],
) -> str:
    compact = [
        {
            "id": r["id"],
            "name": r["name"],
            "locality": r["locality"],
            "city": r["city"],
            "cuisines": r["cuisines"],
            "rating": r["rating"],
            "cost_for_two": r["cost_for_two"],
            "budget_tier": r["budget_tier"],
            "votes": r["votes"],
            "has_online_order": r.get("has_online_order", ""),
            "has_table_booking": r.get("has_table_booking", ""),
        }
        for r in shortlist
    ]
    return (
        "User preferences:\n"
        f"- location filter: {prefs.location}\n"
        f"- max budget (INR for two): {prefs.budget_max_inr}\n"
        f"- cuisine preference: {prefs.cuisine or '(any)'}\n"
        f"- minimum rating: {prefs.min_rating}\n"
        f"- extra notes: {prefs.extras or '(none)'}\n\n"
        "Shortlist (choose only from these ids):\n"
        f"{json.dumps(compact, ensure_ascii=False)}\n\n"
        "Respond with JSON only:\n"
        '{"summary":"<1-2 sentences overall>",'
        '"recommendations":['
        '{"restaurant_id":"<id from list>","rank":1,"explanation":"<2-3 sentences citing cuisines, rating, cost>"}'
        "]}\n"
        "Pick at most 5 restaurants, best match first. Rank starts at 1."
    )


def _extract_json(text: str) -> dict[str, Any] | None:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    m = re.search(r"\{[\s\S]*\}", text)
    if m:
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            return None
    return None


def _cost_display(cost: float) -> str:
    if cost is None or float(cost) <= 0:
        return "Cost not available"
    return f"₹{int(round(float(cost)))} for two"


def _merge(
    shortlist: list[dict[str, Any]],
    parsed: dict[str, Any],
    cfg: AppConfig,
) -> tuple[list[dict[str, Any]], str]:
    by_id = {str(r["id"]): r for r in shortlist}
    summary = str(parsed.get("summary", "")).strip()
    recs = parsed.get("recommendations") or []
    items: list[dict[str, Any]] = []

    seen_ids = set()
    for rec in recs:
        rid = str(rec.get("restaurant_id", "")).strip()
        if rid not in by_id:
            logger.warning("LLM returned unknown restaurant_id=%s", rid)
            continue
        if rid in seen_ids:
            continue
        seen_ids.add(rid)

        row = by_id[rid]
        tier = str(row.get("budget_tier", "unknown"))
        if tier == "unknown":
            est = "medium"
        else:
            est = tier
        cuisines_list = [
            c.strip()
            for c in str(row.get("cuisines", "")).split(",")
            if c.strip()
        ]
        items.append(
            {
                "id": rid,
                "name": row["name"],
                "cuisines": cuisines_list,
                "rating": float(row["rating"]),
                "estimated_cost": est,
                "cost_display": _cost_display(float(row.get("cost_for_two", 0))),
                "explanation": str(rec.get("explanation", "")).strip(),
                "rank": len(items) + 1,
            }
        )

    # fallback or filling up to 5 if needed
    if len(items) < 5:
        # Fallback: top items from shortlist that weren't already added
        for row in shortlist:
            if len(items) >= 5:
                break
            rid = str(row["id"])
            if rid in seen_ids:
                continue
            seen_ids.add(rid)

            tier = str(row.get("budget_tier", "unknown"))
            est = "medium" if tier == "unknown" else tier
            cuisines_list = [
                c.strip()
                for c in str(row.get("cuisines", "")).split(",")
                if c.strip()
            ]
            items.append(
                {
                    "id": rid,
                    "name": row["name"],
                    "cuisines": cuisines_list,
                    "rating": float(row["rating"]),
                    "estimated_cost": est,
                    "cost_display": _cost_display(float(row.get("cost_for_two", 0))),
                    "explanation": (
                        "Selected based on rating and match to your filters "
                        f"({cfg.prompt_version})."
                    ),
                    "rank": len(items) + 1,
                }
            )
        if not summary and not recs:
            summary = "Showing top matches from the filtered list (LLM parse fallback)."
    return items, summary


def recommend(
    prefs: UserPreferences,
    shortlist: list[dict[str, Any]],
    cfg: AppConfig | None = None,
) -> tuple[dict[str, Any], float]:
    """
    Returns (response_dict, duration_llm_ms).
    response_dict matches §4.2 shape (without meta merged in).
    """
    cfg = cfg or load_config()
    if not shortlist:
        return (
            {
                "summary": "No restaurants matched your filters. Try a broader location or higher budget.",
                "items": [],
            },
            0.0,
        )

    user_prompt = _build_user_prompt(prefs, shortlist)
    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": user_prompt},
    ]

    t0 = time.perf_counter()
    text = chat_completion(messages, cfg)
    duration_ms = (time.perf_counter() - t0) * 1000

    parsed = _extract_json(text)
    if parsed is None:
        logger.warning("Groq JSON parse failed; retrying with stricter instruction")
        messages.append(
            {
                "role": "user",
                "content": "Your last reply was not valid JSON. Reply again with ONLY a JSON object, no markdown.",
            }
        )
        t1 = time.perf_counter()
        text2 = chat_completion(messages, cfg)
        duration_ms += (time.perf_counter() - t1) * 1000
        parsed = _extract_json(text2)

    if parsed is None:
        parsed = {"summary": "", "recommendations": []}

    items, summary = _merge(shortlist, parsed, cfg)
    return (
        {
            "summary": summary
            or "Here are restaurants that fit your preferences.",
            "items": items,
        },
        duration_ms,
    )
