"""
WHAT THIS FILE DOES:
--------------------
Estimates the market size for a startup idea.

HOW IT WORKS:
- Sends the startup idea to Gemini
- Asks it to estimate TAM, SAM, SOM (standard market sizing framework)
  - TAM = Total Addressable Market (entire global market)
  - SAM = Serviceable Addressable Market (realistic segment you can reach)
  - SOM = Serviceable Obtainable Market (what you can realistically capture in yr 1-3)
- Also gives a growth trend and key market drivers
"""

import json
from .gemini_client import ask_groq


def estimate_market_size(startup_idea: str) -> dict:
    """
    Takes a startup idea, returns market size estimates
    """

    prompt = f"""
You are a market sizing expert. Estimate the market opportunity for: "{startup_idea}"

Use realistic, research-backed numbers. Be specific with dollar amounts.

Respond ONLY with a valid JSON object in this exact format, no extra text:
{{
  "tam": {{
    "value": "e.g. $15.2B",
    "description": "What the full global market represents"
  }},
  "sam": {{
    "value": "e.g. $3.1B",
    "description": "Realistic addressable segment"
  }},
  "som": {{
    "value": "e.g. $45M",
    "description": "What a new startup could realistically capture in 3 years"
  }},
  "growth_rate": "e.g. 23% CAGR",
  "market_drivers": ["driver 1", "driver 2", "driver 3"],
  "market_risks": ["risk 1", "risk 2"]
}}
"""

    response = ask_groq(prompt)

    try:
        return json.loads(response)
    except json.JSONDecodeError:
        return {"error": "Could not parse market data", "raw": response}
