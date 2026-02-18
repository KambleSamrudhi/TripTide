import json
import os
from ai_engine import ask_ai, journal_prompt


PROFILE_PATH = "data/user_profile.json"
JOURNEY_PATH = "data/past_journeys.json"
MEMORY_CACHE_PATH = "data/ai_cache.json"


# -----------------------------
# LOAD/SAVE HELPERS
# -----------------------------

def load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


# -----------------------------
# UPDATE USER PREFERENCES BASED ON JOURNAL SENTIMENT
# -----------------------------

def update_preferences_from_journal(entry_text):

    sentiment_raw = ask_ai(journal_prompt(entry_text))

    profile = load_json(PROFILE_PATH)
    if not profile:
        profile = {
            "name": "",
            "traveler_type": "",
            "gender": "",
            "interests": [],
            "budget": "",
            "last_destination": "",
            "positive_keywords": [],
            "negative_keywords": [],
            "favorite_food": [],
            "favorite_themes": [],
            "avoid_themes": []
        }

    # sentiment_ai format:
    # Sentiment: Positive/Neutral/Negative
    # Emotion keywords: ...
    # Topic summary: ...

    sentiment_lower = sentiment_raw.lower()

    # -----------------------------------
    # Extract key insights
    # -----------------------------------

    # We grab emotion keywords
    import re
    emotion_match = re.search(r"emotion.*?:\s*(.*)", sentiment_lower)
    emotion_words = []
    if emotion_match:
        emotion_words = [w.strip() for w in emotion_match.group(1).split(",")]

    # Topic summary
    topic_match = re.search(r"(topic summary|summary).*?:\s*(.*)", sentiment_lower)
    topic = topic_match.group(2).strip() if topic_match else ""

    # -----------------------------------
    # Update memory based on sentiment
    # -----------------------------------

    if "positive" in sentiment_lower:
        for w in emotion_words:
            if w not in profile["positive_keywords"]:
                profile["positive_keywords"].append(w)

        if topic and topic not in profile["favorite_themes"]:
            profile["favorite_themes"].append(topic)

    if "negative" in sentiment_lower:
        for w in emotion_words:
            if w not in profile["negative_keywords"]:
                profile["negative_keywords"].append(w)

        if topic and topic not in profile["avoid_themes"]:
            profile["avoid_themes"].append(topic)

    save_json(PROFILE_PATH, profile)
    return profile


# -----------------------------
# PROFILE ENRICHMENT USING AI
# -----------------------------

def ai_enrich_profile():
    """
    Uses the existing profile + journeys to infer deeper patterns.
    """
    profile = load_json(PROFILE_PATH)
    journeys = load_json(JOURNEY_PATH)

    prompt = f"""
You are Triptide AI.

Analyze this user profile:
{json.dumps(profile, indent=2)}

And these journal entries:
{json.dumps(journeys, indent=2)}

Infer:
- Preferred destination types (beach, mountain, city, cultural)
- Budget expectations
- Safety sensitivity
- Food preferences
- Activity preferences (adventure, chill, photography, nightlife)
- Best travel pace
- AI-generated interest tags

Output in structured JSON:
{{
  "personality": "...",
  "destination_preference": "...",
  "ideal_trip_length": "",
  "preferred_climate": "",
  "activity_preference": [],
  "food_preference": [],
  "ai_tags": []
}}
"""

    ai_response = ask_ai(prompt)

    # Save enriched memory
    save_json(MEMORY_CACHE_PATH, {"profile_enriched": ai_response})
    return ai_response

def update_memory_from_analysis(analysis):
    profile = load_json(PROFILE_PATH)

    # Ensure structure exists
    profile.setdefault("favorite_themes", [])
    profile.setdefault("avoid_themes", [])
    profile.setdefault("positive_keywords", [])
    profile.setdefault("negative_keywords", [])
    profile.setdefault("likes", [])
    profile.setdefault("dislikes", [])
    profile.setdefault("emotional_score_sum", 0)
    profile.setdefault("emotional_entries", 0)

    # -----------------------------
    # 1. Update emotional score
    # -----------------------------
    profile["emotional_score_sum"] += analysis.get("emotion_score", 0)
    profile["emotional_entries"] += 1

    # -----------------------------
    # 2. Add liked themes / activities
    # -----------------------------
    for like in analysis.get("likes", []):
        if like not in profile["likes"]:
            profile["likes"].append(like)

    for theme in analysis.get("themes", []):
        if theme not in profile["favorite_themes"]:
            profile["favorite_themes"].append(theme)

    # -----------------------------
    # 3. Add disliked areas
    # -----------------------------
    for dislike in analysis.get("dislikes", []):
        if dislike not in profile["dislikes"]:
            profile["dislikes"].append(dislike)
            profile["avoid_themes"].append(dislike)

    # -----------------------------
    # 4. Keywords
    # -----------------------------
    for kw in analysis.get("emotion_keywords", []):
        if analysis.get("emotion_score", 0) > 0:
            if kw not in profile["positive_keywords"]:
                profile["positive_keywords"].append(kw)
        else:
            if kw not in profile["negative_keywords"]:
                profile["negative_keywords"].append(kw)

    save_json(PROFILE_PATH, profile)
    return profile

# END
