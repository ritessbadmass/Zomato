"""Groq Cloud chat completion."""

from __future__ import annotations

import os
from typing import Any

from groq import Groq

from restaurant_rec.config import AppConfig, load_config

_client: Groq | None = None


def get_groq_client() -> Groq:
    global _client
    if _client is None:
        if not os.environ.get("GROQ_API_KEY", "").strip():
            raise ValueError("GROQ_API_KEY is not set. Add it to .env in the project root.")
        _client = Groq()
    return _client


def chat_completion(
    messages: list[dict[str, str]],
    cfg: AppConfig | None = None,
) -> str:
    cfg = cfg or load_config()
    client = get_groq_client()
    resp = client.chat.completions.create(
        model=cfg.groq_model,
        messages=messages,
        max_tokens=cfg.groq_max_tokens,
        temperature=cfg.groq_temperature,
    )
    choice = resp.choices[0]
    return choice.message.content or ""
