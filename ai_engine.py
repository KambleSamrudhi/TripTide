import os
import json
import socket
import requests
import subprocess


# ==========================================================
# CHECK INTERNET
# ==========================================================

def has_internet():
    try:
        socket.create_connection(("1.1.1.1", 80), timeout=1)
        return True
    except:
        return False


# ==========================================================
# GROQ AI (PRIMARY)
# ==========================================================

GROQ_KEY = os.getenv("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", "")

def groq_ai(prompt):
    if GROQ_KEY == "":
        return "[GROQ ERROR] Missing GROQ_API_KEY"

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama3-8b-8192",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.6
            },
            timeout=25
        )

        data = response.json()

        if "choices" in data:
            return data["choices"][0]["message"]["content"]

        if "error" in data:
            return f"[GROQ ERROR] {data['error']['message']}"

        return "[GROQ UNKNOWN RESPONSE]"

    except Exception as e:
        return f"[GROQ EXCEPTION] {str(e)}"


# ==========================================================
# OLLAMA 2B LOCAL MODEL (FALLBACK)
# ==========================================================

def local_ai(prompt, model="gemma:2b"):
    """
    Calls Ollama locally.
    Must have Ollama installed and model pulled:
       ollama pull gemma:2b
    """

    try:
        result = subprocess.run(
            ["ollama", "run", model],
            input=prompt.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=60
        )

        output = result.stdout.decode("utf-8").strip()
        if output:
            return output
        else:
            return "[LOCAL AI ERROR] No output"

    except FileNotFoundError:
        return "[LOCAL AI ERROR] Ollama not installed"

    except Exception as e:
        return f"[LOCAL AI ERROR] {str(e)}"


# ==========================================================
# UNIFIED AI — ALWAYS CALL THIS
# ==========================================================

def ask_ai(prompt):
    """
    If internet → use Groq  
    If offline → use Ollama gemma 2b  
    """

    if has_internet() and GROQ_KEY != "":
        groq_result = groq_ai(prompt)

        # If Groq fails, fallback to local
        if "ERROR" not in groq_result and "EXCEPTION" not in groq_result:
            return groq_result

        # Groq failed → fallback
        return local_ai(prompt)

    # No internet → local
    return local_ai(prompt)



# ==========================================================
# PROMPT TEMPLATES
# ==========================================================

def itinerary_prompt(destination, days, traveler_type, interests):
    return f"""
Generate a detailed day-by-day travel itinerary.

Destination: {destination}
Days: {days}
Traveler Type: {traveler_type}
Interests: {interests}

Include:
- Morning
- Afternoon
- Evening
- Local tips
- Safety notes
- Food suggestions
- Travel time
- Budget per day

Keep formatting clean.
"""


def packing_prompt(destination, climate, duration, activities, traveler_type):
    return f"""
Create a packing list.

Destination: {destination}
Climate: {climate}
Duration: {duration} days
Activities: {activities}
Traveler Type: {traveler_type}

Include:
- Clothing
- Toiletries
- Tech gear
- Travel essentials
- Safety items
- Optional items
"""


def culture_prompt(destination):
    return f"Write a cultural summary about {destination}. Include history, food, festivals, and traditions."


def safety_prompt(location):
    return f"""
Provide safety analysis for: {location}
Include:
- Risk score
- Concerns
- Safe zones
- Areas to avoid
- Emergency steps
- Gender safety tips
"""


def experiences_prompt(destination, traveler_type):
    return f"""
List 5 authentic local experiences in {destination} for a {traveler_type} traveler.
Include: name, description, price, and duration.
"""


def journal_prompt(entry):
    return f"""
Analyze travel journal entry:

{entry}

Return:
- Sentiment
- Emotions
- Summary
- Personality insight
"""
