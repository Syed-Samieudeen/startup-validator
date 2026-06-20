"""
WHAT THIS FILE DOES:
--------------------
The single connection point to Google's free Gemini LLM API.

HOW IT WORKS:
- Loads your GEMINI_API_KEY from the .env file
- Sends any prompt to Gemini Flash (the free, fast model)
- Authenticates using the X-goog-api-key HEADER (required for newer
  "AQ.xxxx"-format keys — the old "?key=" URL param method gives a 401)
- Returns the text response as a plain Python string
- All 5 tools (competitors, market, reviews, pricing, roadmap) call THIS function
- If the daily/minute rate limit is hit, raises DailyLimitExceeded with a clear message
- If you ever want to switch AI providers again, you only change THIS file

NOTE: The function is still named "ask_groq" on purpose — so none of the
5 tool files (competitors.py, market_size.py, etc.) need to be edited.
They just import ask_groq from here, same as before.
"""

import os
import requests
from dotenv import load_dotenv

# Load the .env file so GEMINI_API_KEY is available as an environment variable
load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Gemini 2.5 Flash-Lite — Google's current (as of mid-2026), actively
# supported model with the highest free tier quota. We previously tried
# gemini-2.0-flash, but that model was OFFICIALLY RETIRED on June 1, 2026
# and silently redirects to gemini-3.5-flash (which only gets 20 free
# requests/day) — that redirect was the real cause of our earlier 429s.
# 2.5 Flash-Lite is Google's actively maintained low-cost/high-quota model.
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.5-flash-lite:generateContent"
)


class DailyLimitExceeded(Exception):
    """
    Custom exception raised when Gemini's rate limit is hit.
    Caught in app.py and turned into a user-friendly error message.
    """
    pass


def ask_groq(prompt: str, temperature: float = 0.7) -> str:
    """
    Sends a prompt to Google's Gemini 2.0 Flash model.
    (Function kept as "ask_groq" so the rest of the codebase needs zero changes.)

    Args:
        prompt: The full instruction + context string
        temperature: 0.0 = deterministic, 1.0 = creative (0.7 is balanced)

    Returns:
        The model's response as a plain string

    Raises:
        DailyLimitExceeded: if Gemini's free tier limit is hit
    """

    # IMPORTANT: newer Gemini keys (format "AQ.xxxx") require the key to be
    # sent as a HEADER, not as a "?key=" URL parameter. Sending it as a URL
    # param causes a 401 UNAUTHENTICATED error even with a valid key.
    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": GEMINI_API_KEY,
    }

    # Gemini's request format is different from Groq's — this builds it correctly
    body = {
        "contents": [
            {
                "parts": [
                    {
                        "text": (
                            "You are a startup analyst. Always respond with valid JSON only. "
                            "No markdown, no explanation, just the JSON object.\n\n" + prompt
                        )
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": 2000,
        },
    }

    response = requests.post(GEMINI_URL, headers=headers, json=body)

    # Print the FULL response so we can see Google's actual error in the terminal
    if response.status_code != 200:
        print(f"\n⚠️  GEMINI ERROR — status code: {response.status_code}")
        print(f"⚠️  GEMINI ERROR — full response: {response.text}\n")

    # Gemini returns 429 when the free tier rate limit is exceeded
    if response.status_code == 429:
        raise DailyLimitExceeded(
            "The app has hit its free daily AI limit. Please try again tomorrow — "
            "limits reset every 24 hours."
        )

    response.raise_for_status()
    data = response.json()

    # Log which model ACTUALLY served this request. If Google silently
    # redirects our requested model to a different one (as happened with
    # the retired gemini-2.0-flash), this line makes that visible in the
    # logs immediately instead of us discovering it via mystery 429s.
    actual_model = data.get("modelVersion", "unknown")
    print(f"✅ Gemini responded using model: {actual_model}")

    # Extract just the text content from Gemini's response structure
    text = data["candidates"][0]["content"]["parts"][0]["text"]

    # Gemini sometimes wraps JSON in ```json ... ``` markdown fences — strip them
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return text.strip()
