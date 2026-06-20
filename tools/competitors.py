"""
WHAT THIS FILE DOES:
--------------------
Finds competitors for a startup idea.

HOW IT WORKS:
- Sends the startup idea to Gemini
- Asks it to think like a market analyst
- Returns a structured list of competitors with details
- Each competitor has: name, description, estimated users, pricing model
"""

import json
from .gemini_client import ask_groq


def find_competitors(startup_idea: str) -> dict:
    """
    Takes a startup idea string like "AI fitness app"
    Returns a dict with a list of competitors
    """

    prompt = f"""
You are a startup market research analyst. A founder wants to build: "{startup_idea}"

List the TOP 5 direct competitors that already exist in this market.

Respond ONLY with a valid JSON object in this exact format, no extra text:
{{
  "competitors": [
    {{
      "name": "App/Company Name",
      "description": "What they do in one sentence",
      "estimated_users": "e.g. 10M+",
      "pricing": "e.g. Free + $9.99/mo Premium",
      "strengths": "Key advantage",
      "weakness": "Main gap or weakness"
    }}
  ]
}}
"""

    response = ask_groq(prompt)

    try:
        # Gemini returns a string — we parse it into a Python dict
        data = json.loads(response)
        return data
    except json.JSONDecodeError:
        # If parsing fails, return raw text wrapped in a dict
        return {"competitors": [], "raw": response}
