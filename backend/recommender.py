"""
LLM-powered restaurant ranking via Groq (llama-3.3-70b-versatile).
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from groq import Groq

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

_client: Groq | None = None


def _get_client() -> Groq:
    global _client
    if _client is None:
        api_key = os.environ.get("GROQ_API_KEY", "")
        if not api_key:
            raise ValueError("GROQ_API_KEY is not set in the environment.")
        _client = Groq(api_key=api_key)
    return _client


SYSTEM_PROMPT = (
    "You are a knowledgeable and friendly restaurant recommendation assistant "
    "for an app like Zomato. You help users find the best restaurants based on "
    "their preferences. Always be specific, helpful, and explain your reasoning "
    "clearly. Format your response strictly as valid JSON."
)


def _build_user_prompt(user_preferences: dict[str, Any], restaurants: list[dict]) -> str:
    loc = user_preferences.get("location", "")
    budget = user_preferences.get("budget", "")
    cuisine = user_preferences.get("cuisine", "")
    min_rating = user_preferences.get("min_rating", "")
    extra = user_preferences.get("extra_preferences", "") or ""

    lines = [
        "A user is looking for restaurant recommendations with these preferences:",
        f"- Location: {loc}",
        f"- Budget: {budget}",
        f"- Cuisine: {cuisine}",
        f"- Minimum Rating: {min_rating}",
        f"- Additional Preferences: {extra}",
        "",
        "Here are the available restaurants that match their criteria:",
        "",
    ]
    for i, r in enumerate(restaurants, start=1):
        lines.append(f"{i}. {r.get('restaurant_name', '')}")
        lines.append(f"   Location: {r.get('location', '')}")
        lines.append(f"   Cuisines: {r.get('cuisines', '')}")
        lines.append(f"   Average cost (for two): {r.get('avg_cost', '')}")
        lines.append(f"   Rating: {r.get('rating', '')}")
        lines.append(f"   Votes: {r.get('votes', '')}")
        lines.append(f"   Online order: {r.get('has_online_order', '')}")
        lines.append(f"   Table booking: {r.get('has_table_booking', '')}")
        lines.append("")

    lines.extend(
        [
            "Please:",
            "1. Select the top 5 restaurants from the list above (or fewer if less "
            "than 5 are available).",
            "2. Rank them from best to worst fit for the user.",
            "3. For each restaurant, write a 2-3 sentence personalized explanation "
            "of why it suits this user's preferences.",
            "4. If relevant, mention online ordering or table booking availability.",
            "5. Respond ONLY with a valid JSON object in this exact format:",
            "{",
            '  "recommendations": [',
            "    {",
            '      "rank": 1,',
            '      "restaurant_name": "...",',
            '      "location": "...",',
            '      "cuisines": "...",',
            '      "avg_cost": 0,',
            '      "rating": 0,',
            '      "has_online_order": "...",',
            '      "has_table_booking": "...",',
            '      "explanation": "..."',
            "    }",
            "  ],",
            '  "summary": "A 1-2 sentence overall summary of the recommendations."',
            "}",
            "Do not include any text outside the JSON object.",
        ]
    )
    return "\n".join(lines)


def _extract_json_object(text: str) -> str | None:
    m = re.search(r"\{[\s\S]*\}", text)
    return m.group(0) if m else None


def get_llm_recommendations(
    user_preferences: dict,
    restaurants: list[dict],
) -> dict[str, Any]:
    if not restaurants:
        return {
            "recommendations": [],
            "summary": "No restaurants to analyze.",
        }

    user_message = _build_user_prompt(user_preferences, restaurants)
    client = _get_client()

    chat_completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        max_tokens=2000,
        temperature=0.7,
    )

    raw_text = chat_completion.choices[0].message.content or ""

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        pass

    extracted = _extract_json_object(raw_text)
    if extracted:
        try:
            return json.loads(extracted)
        except json.JSONDecodeError:
            pass

    return {
        "recommendations": [
            {
                "rank": i + 1,
                "restaurant_name": r.get("restaurant_name", ""),
                "location": r.get("location", ""),
                "cuisines": r.get("cuisines", ""),
                "avg_cost": r.get("avg_cost", 0),
                "rating": r.get("rating", 0),
                "has_online_order": str(r.get("has_online_order", "")),
                "has_table_booking": str(r.get("has_table_booking", "")),
                "explanation": "Shown as fallback because the AI response could not be parsed as JSON.",
            }
            for i, r in enumerate(restaurants[:5])
        ],
        "summary": (
            "Could not parse the model response as JSON. Raw response excerpt: "
            + raw_text[:500]
        ),
    }
