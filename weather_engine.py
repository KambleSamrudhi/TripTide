import requests
import socket
import json
import os


# Load offline weather fallback
def load_defaults():
    path = os.path.join("data", "weather_defaults.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

defaults = load_defaults()


def has_internet():
    try:
        socket.create_connection(("1.1.1.1", 80), timeout=1)
        return True
    except:
        return False


# -------- ONLINE WEATHER (REALTIME via Open-Meteo) --------

def get_weather_online(lat, lon):
    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}&current_weather=true"
        )

        resp = requests.get(url, timeout=3)
        data = resp.json()

        temp = data["current_weather"]["temperature"]
        wind = data["current_weather"]["windspeed"]
        code = data["current_weather"]["weathercode"]

        # Convert code → text
        conditions = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Foggy",
            48: "Depositing rime fog",
            51: "Light drizzle",
            61: "Light rain",
            71: "Snowfall",
            80: "Rain showers",
            95: "Thunderstorm"
        }

        condition = conditions.get(code, "Unknown weather")

        return {
            "temp": temp,
            "wind": wind,
            "condition": condition
        }

    except:
        return None


# -------- OFFLINE WEATHER BACKUP --------

def offline_weather():
    return {
        "temp": defaults.get("fallback_temp", 28),
        "wind": 5,
        "condition": defaults.get("fallback_condition", "Partly Cloudy")
    }


# -------- MAIN WEATHER ACCESS --------

def get_weather(lat, lon):
    if has_internet():
        online = get_weather_online(lat, lon)
        if online:
            return online

    return offline_weather()
