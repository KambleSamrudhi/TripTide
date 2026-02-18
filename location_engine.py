import requests
import socket

# ------------------------------------
# CHECK INTERNET
# ------------------------------------

def has_internet():
    try:
        socket.create_connection(("1.1.1.1", 80), timeout=1)
        return True
    except:
        return False


# ------------------------------------
# ONLINE LOCATION DETECTION
# ------------------------------------

def get_location_online():
    try:
        resp = requests.get("https://ipapi.co/json/", timeout=3)
        data = resp.json()

        return {
            "status": "online",
            "city": data.get("city", ""),
            "region": data.get("region", ""),
            "country": data.get("country_name", ""),
            "latitude": data.get("latitude", 0.0),
            "longitude": data.get("longitude", 0.0)
        }

    except:
        return None


# ------------------------------------
# OFFLINE LOCATION FALLBACK
# ------------------------------------

def offline_location():
    return {
        "status": "offline",
        "city": "Unknown",
        "region": "Unknown",
        "country": "Offline Mode",
        "latitude": 0.0,
        "longitude": 0.0
    }


# ------------------------------------
# MAIN ACCESS POINT
# ------------------------------------

def get_user_location():
    if has_internet():
        loc = get_location_online()
        if loc:
            return loc
    return offline_location()
