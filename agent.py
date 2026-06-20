"""
WHAT THIS FILE DOES:
--------------------
The Agent Orchestrator — runs all 5 analysis tools in order.

HOW IT WORKS:
1. Takes your startup idea as input
2. Calls competitors.py  → finds who you're up against
3. Calls market_size.py  → estimates how big the market is
4. Calls reviews.py      → finds user pain points in competitor apps
5. Calls pricing.py      → recommends your pricing tiers
6. Calls roadmap.py      → generates your phased build plan
7. Returns everything as one big dict (sent to frontend as JSON)

Think of this as an assembly line:
startup_idea → [tool1] → [tool2] → [tool3] → [tool4] → [tool5] → full report
"""

from tools.competitors import find_competitors
from tools.market_size import estimate_market_size
from tools.reviews import analyze_reviews
from tools.pricing import suggest_pricing
from tools.roadmap import generate_roadmap


def run_validation(startup_idea: str) -> dict:
    """
    Main agent function. Call this with any startup idea string.
    Returns the complete validation report as a Python dict.
    """

    print(f"\n🚀 Starting validation for: '{startup_idea}'")
    report = {"startup_idea": startup_idea}

    # ── STEP 1: Find Competitors ──────────────────────────────────────
    print("🔍 Step 1/5: Finding competitors...")
    competitor_data = find_competitors(startup_idea)
    competitors = competitor_data.get("competitors", [])
    report["competitors"] = competitors

    # ── STEP 2: Estimate Market Size ─────────────────────────────────
    print("📊 Step 2/5: Estimating market size...")
    market_data = estimate_market_size(startup_idea)
    report["market_size"] = market_data

    # ── STEP 3: Analyze Reviews ───────────────────────────────────────
    print("💬 Step 3/5: Analyzing user reviews...")
    review_data = analyze_reviews(startup_idea, competitors)
    report["reviews"] = review_data

    # ── STEP 4: Suggest Pricing ───────────────────────────────────────
    print("💰 Step 4/5: Designing pricing strategy...")
    pricing_data = suggest_pricing(startup_idea, competitors)
    report["pricing"] = pricing_data

    # ── STEP 5: Generate MVP Roadmap ──────────────────────────────────
    print("🗺️  Step 5/5: Building MVP roadmap...")

    # Pass unmet_needs from reviews into roadmap for smarter recommendations
    unmet_needs = review_data.get("unmet_needs", [])
    pricing_model = pricing_data.get("recommended_model", "Freemium")
    roadmap_data = generate_roadmap(startup_idea, unmet_needs, pricing_model)
    report["roadmap"] = roadmap_data

    print("✅ Validation complete!\n")
    return report
