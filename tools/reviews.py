"""
WHAT THIS FILE DOES:
--------------------
Analyzes what users love/hate about existing competitor apps.

HOW IT WORKS:
- Since we can't scrape App Store reviews in real-time without an API,
  we use Gemini's training knowledge of real app reviews
- Asks Gemini to summarize common user sentiments for competitor apps
- Returns: pain points, loved features, and opportunity gaps
- These gaps = your startup's competitive advantages
"""

import json
from .gemini_client import ask_groq


def analyze_reviews(startup_idea: str, competitors: list) -> dict:
    """
    Takes a startup idea + list of competitor names
    Returns analysis of user sentiment and gaps in the market
    """

    # Extract just the names from competitor dicts
    competitor_names = [c.get("name", "") for c in competitors]
    competitors_str = ", ".join(competitor_names) if competitor_names else "existing apps in this space"

    prompt = f"""
You are a UX researcher who has analyzed thousands of App Store and Google Play reviews.

Startup idea: "{startup_idea}"
Known competitors: {competitors_str}

Based on common user feedback patterns for apps in this category, analyze:

Respond ONLY with a valid JSON object in this exact format, no extra text:
{{
  "top_complaints": [
    {{"issue": "complaint description", "frequency": "e.g. 67% of negative reviews", "competitor": "which app"}}
  ],
  "top_praises": [
    {{"feature": "what users love", "frequency": "e.g. mentioned in 40% of reviews"}}
  ],
  "unmet_needs": [
    "Gap 1: what users keep asking for but nobody delivers",
    "Gap 2: another unmet need",
    "Gap 3: another unmet need"
  ],
  "sentiment_summary": "2-sentence overall summary of user sentiment in this market",
  "opportunity_score": "e.g. 7.5/10",
  "opportunity_reason": "Why this score — what the data suggests for a new entrant"
}}
"""

    response = ask_groq(prompt)

    try:
        return json.loads(response)
    except json.JSONDecodeError:
        return {"error": "Could not parse review data", "raw": response}
