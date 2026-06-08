from __future__ import annotations

import json

from app.config import settings


def explain(symbol: str, persona_name: str, evaluation: dict) -> str:
    cache_key = f"explain:{symbol}:{persona_name}:{evaluation.get('summary', {}).get('verdict')}"
    try:
        import redis

        client = redis.from_url(settings.redis_url, decode_responses=True)
        cached = client.get(cache_key)
        if cached:
            return cached
    except Exception:
        client = None

    failures = [e["criterion"] for e in evaluation.get("evaluations", []) if e["status"] == "fail"]
    fallback = (
        f"{symbol} {'passes' if not failures else 'fails'} {persona_name}'s hard-filter workflow. "
        f"{'All mandatory criteria are currently satisfied' if not failures else 'The blocking criteria are: ' + ', '.join(failures)}. "
        "Under the rule set, one hard-filter failure is enough to reject the stock or trigger a sell alert in the portfolio."
    )
    text = fallback
    if settings.anthropic_api_key:
        try:
            from anthropic import Anthropic

            client_ai = Anthropic(api_key=settings.anthropic_api_key)
            message = client_ai.messages.create(
                model="claude-3-5-sonnet-latest",
                max_tokens=180,
                messages=[
                    {
                        "role": "user",
                        "content": (
                            "Explain in exactly 3 plain-English sentences why this NSE stock passed or failed. "
                            f"Stock: {symbol}. Persona: {persona_name}. Evaluation JSON: {json.dumps(evaluation)[:5000]}"
                        ),
                    }
                ],
            )
            text = message.content[0].text
        except Exception:
            text = fallback
    try:
        if client:
            client.setex(cache_key, 24 * 60 * 60, text)
    except Exception:
        pass
    return text
