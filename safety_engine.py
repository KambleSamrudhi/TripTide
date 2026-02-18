import json
import os
import requests
import socket
from ai_engine import ask_ai, safety_prompt


# ---------------------------------------------------
# INTERNET CHECK
# ---------------------------------------------------

def has_internet():
    try:
        socket.create_connection(("1.1.1.1", 80), timeout=1)
        return True
    except:
        return False


# ---------------------------------------------------
# LOAD LOCAL SAFETY DB
# ---------------------------------------------------

def load_safety_local():
    path = os.path.join("data", "safety.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


local_safety_data = load_safety_local()


# ---------------------------------------------------
# LOOKUP SAFETY FROM LOCAL DB
# ---------------------------------------------------

def get_local_safety(location):
    for entry in local_safety_data:
        if entry["location"].lower() == location.lower():
            return entry
    return None


# ---------------------------------------------------
# ONLINE REALTIME SAFETY ALERTS (NEWS API-LIKE)
# FREE API ALTERNATIVE USING GNEWS RSS FEED
# ---------------------------------------------------

def get_online_alerts(location):
    if not has_internet():
        return None

    try:
        url = f"https://gnews.io/api/v4/search?q={location}+travel+safety&lang=en&max=5&token=demo"
        # NOTE: token=demo returns limited free sample — offline fallback handles the rest
        
        r = requests.get(url, timeout=4)
        data = r.json()

        if "articles" in data:
            alerts = [{
                "title": a["title"],
                "description": a["description"],
                "url": a["url"]
            } for a in data["articles"]]
        else:
            alerts = []

        return alerts

    except:
        return None


# ---------------------------------------------------
# AI-BASED SAFETY ASSESSMENT
# ---------------------------------------------------

def ai_safety_analysis(location, gender, traveler_type):
    """
    Adds AI interpretation: safety level, areas to avoid,
    gender-specific tips, emergency guidance.
    """

    prompt = f"""
You are Triptide Safety AI.

Analyze safety for:
Location: {location}
Traveler Type: {traveler_type}
Gender: {gender}

Provide structured JSON:
{{
  "risk_level": "",
  "why": "",
  "safe_areas": [],
  "avoid_areas": [],
  "gender_specific_tips": [],
  "solo_traveler_mode": [],
  "emergency_guidance": ""
}}
"""

    response = ask_ai(prompt)

    # fallback if AI doesn't return valid JSON
    try:
        return json.loads(response)
    except:
        return {
            "risk_level": "Unknown",
            "why": response,
            "safe_areas": [],
            "avoid_areas": [],
            "gender_specific_tips": [],
            "solo_traveler_mode": [],
            "emergency_guidance": "Contact nearest embassy"
        }


# ---------------------------------------------------
# EMERGENCY AI MODE
# ---------------------------------------------------

def ai_emergency_help(situation, location):
    prompt = f"""
You are Triptide Emergency Assistant.

Situation:
{situation}

Location: {location}

Provide concise emergency instructions:
- Immediate steps
- Who to contact
- Safety precautions
- How to get help
- If offline: what to do
"""

    return ask_ai(prompt)


# ---------------------------------------------------
# COMBINED SAFETY ENGINE
# ---------------------------------------------------

def safety_engine(location, gender, traveler_type):
    """
    Main safety function combining:
    - Local safety DB
    - AI safety interpretation
    - Online alerts (if available)
    """

    local = get_local_safety(location)
    ai_result = ai_safety_analysis(location, gender, traveler_type)
    online_alerts = get_online_alerts(location)

    return {
        "local_data": local,
        "ai_analysis": ai_result,
        "alerts": online_alerts if online_alerts else "offline"
    }
