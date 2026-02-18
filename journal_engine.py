import json
import os
from ai_engine import ask_ai, journal_prompt


# -----------------------------
# MAIN ANALYZER
# -----------------------------

def analyze_journal_entry(text):
    """
    Returns a detailed emotional + thematic analysis
    using the local/online AI engine.
    """

    prompt = f"""
Analyze this travel journal entry in deep detail:

Entry:
\"\"\"{text}\"\"\"

Provide structured JSON in this format:
{{
  "sentiment": "positive/neutral/negative",
  "emotion_keywords": ["happy", "excited"],
  "emotion_score": -5 to +5,
  "themes": ["food", "culture", "nature"],
  "activity_mentions": ["beach", "festival"],
  "likes": ["sunset", "local food"],
  "dislikes": ["crowds", "heat"],
  "summary": "One-sentence emotional summary"
}}
"""

    response = ask_ai(prompt)

    # Try to return parsed JSON — AI may give text, so fallback
    try:
        parsed = json.loads(response)
        return parsed
    except:
        # fallback minimal analysis
        return {
            "sentiment": "unknown",
            "emotion_keywords": [],
            "emotion_score": 0,
            "themes": [],
            "activity_mentions": [],
            "likes": [],
            "dislikes": [],
            "summary": response
        }
