"""
WHAT THIS FILE DOES:
--------------------
Generates a practical MVP (Minimum Viable Product) roadmap.

HOW IT WORKS:
- Takes all prior analysis as context (competitors, gaps, pricing)
- Asks Gemini to design a phased build plan
- Phase 1 = MVP (build in weeks, launch fast)
- Phase 2 = Growth (after first users)
- Phase 3 = Scale (after product-market fit)
- Also gives tech stack recommendation and first milestone target
"""

import json
from .gemini_client import ask_groq


def generate_roadmap(startup_idea: str, unmet_needs: list, pricing_model: str) -> dict:
    """
    Takes startup idea + market gaps + pricing model
    Returns a phased MVP roadmap
    """

    needs_str = "\n".join(f"- {n}" for n in unmet_needs) if unmet_needs else "- General improvements over competitors"

    prompt = f"""
You are a startup CTO and product strategist. Create an MVP roadmap.

Startup idea: "{startup_idea}"
Key unmet needs to solve:
{needs_str}
Planned pricing model: {pricing_model}

Build a practical, realistic roadmap for a solo founder or small team.

Respond ONLY with a valid JSON object in this exact format, no extra text:
{{
  "mvp_summary": "One sentence describing the core MVP",
  "phases": [
    {{
      "phase": "Phase 1: MVP",
      "duration": "e.g. 6-8 weeks",
      "goal": "What success looks like at end of this phase",
      "features": ["feature 1", "feature 2", "feature 3", "feature 4"],
      "milestone": "e.g. 100 beta users"
    }},
    {{
      "phase": "Phase 2: Growth",
      "duration": "e.g. Month 3-5",
      "goal": "What success looks like",
      "features": ["feature 1", "feature 2", "feature 3"],
      "milestone": "e.g. $1K MRR"
    }},
    {{
      "phase": "Phase 3: Scale",
      "duration": "e.g. Month 6-12",
      "goal": "What success looks like",
      "features": ["feature 1", "feature 2", "feature 3"],
      "milestone": "e.g. $10K MRR"
    }}
  ],
  "recommended_stack": {{
    "frontend": "e.g. React Native (iOS + Android)",
    "backend": "e.g. Python FastAPI",
    "database": "e.g. PostgreSQL + Redis",
    "ai_layer": "e.g. Gemini API for real-time AI features",
    "hosting": "e.g. Render.com (free tier)"
  }},
  "first_action": "The single most important thing to do THIS WEEK"
}}
"""

    response = ask_groq(prompt)

    try:
        return json.loads(response)
    except json.JSONDecodeError:
        return {"error": "Could not parse roadmap data", "raw": response}
