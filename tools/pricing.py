"""
WHAT THIS FILE DOES:
--------------------
Suggests smart pricing strategy for your startup.

HOW IT WORKS:
- Takes competitor pricing data as context
- Asks Gemini to design a pricing model that can compete and win
- Returns: freemium tier, paid tiers, pricing rationale
- Also suggests which pricing psychology tactics to use
"""

import json
from .gemini_client import ask_groq


def suggest_pricing(startup_idea: str, competitors: list) -> dict:
    """
    Takes startup idea + competitor list
    Returns recommended pricing tiers and strategy
    """

    # Build a summary of competitor pricing for context
    competitor_pricing = []
    for c in competitors:
        name = c.get("name", "Unknown")
        pricing = c.get("pricing", "Unknown")
        competitor_pricing.append(f"{name}: {pricing}")

    pricing_context = "\n".join(competitor_pricing) if competitor_pricing else "No competitor pricing data"

    prompt = f"""
You are a SaaS pricing strategist. Design the optimal pricing model for a new startup.

Startup idea: "{startup_idea}"

Competitor pricing:
{pricing_context}

Design a pricing strategy that can attract users AND be profitable.

Respond ONLY with a valid JSON object in this exact format, no extra text:
{{
  "recommended_model": "e.g. Freemium with Premium tiers",
  "tiers": [
    {{
      "name": "Free",
      "price": "$0/month",
      "features": ["feature 1", "feature 2", "feature 3"],
      "target": "Who this tier is for"
    }},
    {{
      "name": "Pro",
      "price": "$X/month",
      "features": ["feature 1", "feature 2", "feature 3"],
      "target": "Who this tier is for"
    }},
    {{
      "name": "Elite",
      "price": "$X/month",
      "features": ["feature 1", "feature 2", "feature 3"],
      "target": "Who this tier is for"
    }}
  ],
  "pricing_strategy": "2-sentence explanation of the pricing logic",
  "conversion_tactic": "Key psychological tactic to drive free-to-paid conversion",
  "annual_discount": "e.g. 20% off for annual billing",
  "ltv_estimate": "Estimated lifetime value of one paying customer"
}}
"""

    response = ask_groq(prompt)

    try:
        return json.loads(response)
    except json.JSONDecodeError:
        return {"error": "Could not parse pricing data", "raw": response}
