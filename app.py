"""
WHAT THIS FILE DOES:
--------------------
The Flask Web Server — the entry point of the whole app.

HOW IT WORKS:
- Route GET  /          → serves the HTML dashboard (index.html)
- Route POST /validate  → receives startup idea, runs agent, returns JSON report

When you run `python app.py`, Flask starts a local web server at:
  http://localhost:5000

The frontend (index.html) sends a POST request to /validate with the idea,
Flask passes it to agent.py, gets the full report back, and returns it as JSON.
"""

from flask import Flask, render_template, request, jsonify
from agent import run_validation
from tools.gemini_client import DailyLimitExceeded

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/validate", methods=["POST"])
def validate():
    """
    POST /validate
    Body: { "idea": "I want to build an AI fitness app" }

    1. Extracts the idea from the request body
    2. Passes it to the agent orchestrator
    3. Returns the full report as JSON to the frontend

    ERROR HANDLING:
    - DailyLimitExceeded → 429 with a friendly "try tomorrow" message
    - Any other exception → 500 with the error text
    """

    data = request.get_json()

    if not data or not data.get("idea"):
        return jsonify({"error": "No startup idea provided"}), 400

    startup_idea = data["idea"].strip()

    if len(startup_idea) < 5:
        return jsonify({"error": "Please describe your idea in more detail"}), 400

    try:
        report = run_validation(startup_idea)
        return jsonify(report)

    except DailyLimitExceeded as e:
        # Caught specifically so the frontend can show the rate-limit UI
        return jsonify({
            "error": str(e),
            "error_type": "rate_limit"
        }), 429

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
