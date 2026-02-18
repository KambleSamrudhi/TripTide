from flask import Flask, render_template, request, jsonify, redirect

import json
import time
import os
import csv
from flask import Response
from geopy.distance import geodesic
from flask import send_from_directory

from ai_engine import (
    ask_ai,
    itinerary_prompt,
    packing_prompt,
    culture_prompt,
    safety_prompt,
    experiences_prompt,
    journal_prompt
)

from memory_engine import (
    update_preferences_from_journal,
    ai_enrich_profile
)

from safety_engine import (
    safety_engine,
    ai_emergency_help,
    get_local_safety
)

from journal_engine import analyze_journal_entry

from memory_engine import (
    update_memory_from_analysis,
    ai_enrich_profile
)

# -------------------------------------------------------
# NEW ANALYTICS ENGINE — 100% working
# -------------------------------------------------------
from analytics_engine import (
    load_analytics,
    save_analytics,
    log_page,
    log_load_time,
    log_scroll,
    log_ai,
    log_click,
    log_task_attempt,
    log_task_success,
    log_task_error,
    submit_sus,
    submit_nps,
    compute_metrics,
    compute_tsr,
    compute_uer,


)

from location_engine import get_user_location
from weather_engine import get_weather


app = Flask(
    __name__,
    static_folder="static",
    template_folder="templates"
)

# -------------------------------------------------------
# DEBUG HELPER (renamed to avoid conflict)
# -------------------------------------------------------
def debug_loaded(page=""):
    print(f"Loaded: {page}")

# Safe JSON response
def ok():
    return jsonify({"status": "ok"})


# -------------------------------------------------------
# JSON HELPERS
# -------------------------------------------------------
def load_json(name):
    path1 = os.path.join("data", name)
    if os.path.exists(path1):
        with open(path1, "r", encoding="utf-8") as f:
            return json.load(f)

    path2 = os.path.join("static", "data", name)
    if os.path.exists(path2):
        with open(path2, "r", encoding="utf-8") as f:
            return json.load(f)

    return {}


def save_json(name, data):
    path = os.path.join("data", name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f)


# -------------------------------------------------------
# DISABLE OLD BROKEN ANALYTICS
# -------------------------------------------------------
def increment_metric(section, key, amount=1):
    return

def increment_counter(key, amount=1):
    return


# -------------------------------------------------------
# ROUTES — UI PAGES
# -------------------------------------------------------
@app.route("/")
def onboarding():
    return render_template("onboarding.html", timestamp=time.time())

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/explore")
def explore():
    return render_template("explore.html")

@app.route("/planner")
def planner_page():
    return render_template("planner.html")

@app.route("/safety")
def safety_page():
    return render_template("safety.html")

@app.route("/packing")
def packing_page():
    return render_template("packing.html")

@app.route("/stories")
def stories_page():
    return render_template("stories.html")

@app.route("/locals")
def locals_page():
    return render_template("locals.html")

@app.route("/admin")
def admin_dashboard():
    return render_template("admin.html")


# -------------------------------------------------------
# PROFILE
# -------------------------------------------------------
@app.route("/api/save_profile", methods=["POST"])
def save_profile():
    data = request.json
    save_json("user_profile.json", data)
    return jsonify({"status": "ok", "saved": True})


@app.route("/api/get_profile")
def get_profile():
    profile = load_json("user_profile.json")
    return jsonify(profile)


# -------------------------------------------------------
# ITINERARY
# -------------------------------------------------------
@app.route("/api/itinerary", methods=["POST"])
def itinerary():
    req = request.json

    prompt = itinerary_prompt(
        req["destination"],
        req["days"],
        req["traveler_type"],
        req["interests"]
    )

    response = ask_ai(prompt)
    return jsonify({"itinerary": response})


# -------------------------------------------------------
# PACKING
# -------------------------------------------------------
@app.route("/api/packing", methods=["POST"])
def packing_ai():
    req = request.json

    prompt = packing_prompt(
        req["destination"],
        req["climate"],
        req["duration"],
        req["activities"],
        req["traveler_type"]
    )

    response = ask_ai(prompt)
    return jsonify({"packing_list": response})


# -------------------------------------------------------
# CULTURAL STORYTELLING
# -------------------------------------------------------
@app.route("/api/culture", methods=["POST"])
def culture_ai():
    req = request.json
    prompt = culture_prompt(req["destination"])
    response = ask_ai(prompt)
    return jsonify({"story": response})


# -------------------------------------------------------
# SAFETY
# -------------------------------------------------------
@app.route("/api/safety_check", methods=["POST"])
def safety_check():
    req = request.json
    prompt = safety_prompt(req["location"])
    response = ask_ai(prompt)
    return jsonify({"safety": response})


@app.route("/api/safety/enhanced", methods=["POST"])
def enhanced_safety():
    req = request.json

    location = req["location"]
    gender = req["gender"]
    traveler_type = req["traveler_type"]

    data = safety_engine(location, gender, traveler_type)
    return jsonify(data)


@app.route("/api/safety/emergency", methods=["POST"])
def emergency_help():
    req = request.json
    situation = req["situation"]
    location = req["location"]

    response = ai_emergency_help(situation, location)
    return jsonify({"advice": response})


@app.route("/api/safety/region", methods=["POST"])
def region_safety():
    req = request.json
    location = req["location"]

    local = get_local_safety(location)
    return jsonify(local if local else {"score": "unknown"})


# -------------------------------------------------------
# EXPERIENCES
# -------------------------------------------------------
@app.route("/api/local_experiences", methods=["POST"])
def ai_experiences():
    req = request.json
    prompt = experiences_prompt(req["destination"], req["traveler_type"])
    response = ask_ai(prompt)
    return jsonify({"experiences": response})


# -------------------------------------------------------
# JOURNAL
# -------------------------------------------------------
@app.route("/journal")
def journal_page():
    entries = load_json("journal.json")
    return render_template("journal.html", entries=entries)


@app.route("/journal/new")
def journal_new_page():
    return render_template("new_journal.html")


@app.route("/journal/save", methods=["POST"])
def journal_save():
    data = request.json

    all_entries = load_json("journal.json")
    new_id = len(all_entries) + 1

    entry = {
        "id": new_id,
        "text": data["text"],
        "date": data["date"],
        "image": data.get("image", "")
    }

    all_entries.append(entry)
    save_json("journal.json", all_entries)

    return jsonify({"status": "ok"})


@app.route("/api/journal/all")
def get_journals():
    entries = load_json("journal.json")
    return jsonify(entries)


# -------------------------------------------------------
# LOCATION & WEATHER
# -------------------------------------------------------
@app.route("/api/location")
def get_location():
    loc = get_user_location()
    return jsonify(loc)

@app.route("/api/weather")
def weather():
    loc = get_user_location()

    lat = loc.get("latitude", 0)
    lon = loc.get("longitude", 0)

    weather_data = get_weather(lat, lon)

    return jsonify({
        "location": loc,
        "weather": weather_data
    })


# -------------------------------------------------------
# ADMIN EXPORTS
# -------------------------------------------------------
@app.route("/api/admin/users")
def admin_get_users():
    profile = load_json("user_profile.json")
    return jsonify({"users": [profile]})


@app.route("/api/admin/journeys")
def admin_get_journeys():
    journeys = load_json("past_journeys.json")
    return jsonify({"journeys": journeys})


@app.route("/api/admin/export/users_csv")
def export_users_csv():
    profile = load_json("user_profile.json")

    output = Response()
    output.headers["Content-Disposition"] = "attachment; filename=users.csv"
    output.headers["Content-Type"] = "text/csv"

    writer = csv.writer(output)
    writer.writerow(profile.keys())
    writer.writerow(profile.values())

    return output


@app.route("/api/admin/export/metrics_csv")
def admin_export_metrics_csv():
    data = {**load_analytics(), **compute_metrics()}

    output = Response()
    output.headers["Content-Disposition"] = "attachment; filename=metrics.csv"
    output.headers["Content-Type"] = "text/csv"

    writer = csv.writer(output)
    for key, val in data.items():
        writer.writerow([key, val])

    return output


@app.route("/api/admin/export/json")
def admin_export_json():
    dump = {
        "profile": load_json("user_profile.json"),
        "journeys": load_json("past_journeys.json"),
        "analytics": load_analytics(),
        "computed": compute_metrics()
    }
    return jsonify(dump)


# -------------------------------------------------------
# NEW METRICS LOGGING (100% GOOD)
# -------------------------------------------------------
@app.post("/api/metrics/log_page")
def m_page():
    d = request.json or {}
    log_page(d.get("user", "anonymous"), d.get("page"))
    return {"status": "ok"}

@app.post("/api/metrics/log_load_time")
def m_load():
    d = request.json or {}
    log_load_time(d.get("user", "anonymous"), d.get("page"), d.get("load_time"))
    return {"status": "ok"}

@app.post("/api/metrics/log_scroll")
def m_scroll():
    d = request.json or {}

    page = d.get("page")
    depth = d.get("depth")
    user = d.get("user", "anonymous")

    # ==== SAFETY CHECKS (CRITICAL) ====
    if not page or page is None:
        page = "unknown"

    if depth is None:
        depth = 0

    try:
        log_scroll(user, page, depth)
        return jsonify({"status": "ok"})
    except Exception as e:
        print("SCROLL LOG ERROR:", e)
        return jsonify({"status": "error", "error": str(e)}), 500


@app.post("/api/metrics/log_event")
def m_event():
    d = request.json or {}
    log_click(d.get("user", "anonymous"), d.get("event"))
    return {"status": "ok"}

@app.post("/api/metrics/log_ai")
def m_ai():
    d = request.json or {}
    log_ai(d.get("user", "anonymous"), d.get("source"))
    return {"status": "ok"}

@app.post("/api/metrics/task_attempt")
def m_attempt():
    d = request.json or {}
    log_task_attempt(d.get("user", "anonymous"), d.get("task"))
    return {"status": "ok"}

@app.post("/api/metrics/task_success")
def m_success():
    d = request.json or {}
    log_task_success(d.get("user", "anonymous"), d.get("task"), d.get("duration", 0))
    return {"status": "ok"}

@app.post("/api/metrics/task_error")
def m_error():
    d = request.json or {}
    log_task_error(d.get("user", "anonymous"), d.get("task"))
    return {"status": "ok"}


# -------------------------------------------------------
# FIXED CTR LOGGING
# -------------------------------------------------------
@app.post("/api/metrics/log_ctr")
def api_log_ctr():
    payload = request.json or {}
    label = payload.get("label")
    clicked = payload.get("clicked", 0)

    data = load_analytics()
    ctr = data.setdefault("ctr", {})

    if label not in ctr:
        ctr[label] = {"clicks": 0}

    ctr[label]["clicks"] += int(clicked)
    save_analytics(data)

    return jsonify({"status": "ok"})


# -------------------------------------------------------
# SURVEY SUPPORT
# -------------------------------------------------------
@app.route("/api/survey/submit", methods=["POST"])
def survey_submit():
    data = request.json
    sus_answers = data["sus"]
    nps = int(data["nps"])
    csat = int(data["csat"])

    # Calculate SUS
    sus_scores = []
    for i, val in enumerate(sus_answers):
        score = (val - 1) if i % 2 == 0 else (5 - val)
        sus_scores.append(score)
    final_sus = sum(sus_scores) * 2.5

    save_json("sus.json", {"score": final_sus})
    save_json("nps.json", {"score": nps})
    save_json("csat.json", {"score": csat})

    return jsonify({"status": "ok", "sus": final_sus})


# -------------------------------------------------------
# BACKWARD COMPAT SUS/NPS
# -------------------------------------------------------
@app.route("/api/event", methods=["POST"])
def api_event_simple():
    payload = request.get_json() or {}
    data = load_analytics()
    data.setdefault("events", []).append(payload)
    save_analytics(data)
    return ok()

@app.route("/api/sus", methods=["POST"])
def api_sus_simple():
    payload = request.get_json() or {}
    save_json("sus.json", {"score": payload.get("score", 0)})
    return ok()

@app.route("/api/nps", methods=["POST"])
def api_nps_simple():
    payload = request.get_json() or {}
    save_json("nps.json", {"score": payload.get("score", 0)})
    return ok()


# -------------------------------------------------------
# FINAL — ADMIN METRICS ENDPOINT
# -------------------------------------------------------
@app.route("/api/admin/metrics")
def admin_metrics():
    return compute_metrics()


import os
from datetime import datetime

METRICS_FILE = "triptide/data/metrics_log.txt"

def log_metric(metric_name, value):
    # auto-create file if missing
    os.makedirs(os.path.dirname(METRICS_FILE), exist_ok=True)
    if not os.path.exists(METRICS_FILE):
        open(METRICS_FILE, "w").close()

    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {metric_name}: {value}\n"

    with open(METRICS_FILE, "a", encoding="utf-8") as f:
        f.write(line)

# -------------------------------------------------------
# DESTINATION PAGES
# -------------------------------------------------------
@app.route("/destination/<name>")
def destination_page(name):
    data = load_json("destinations.json")

    all_places = data.get("india", []) + data.get("international", [])

    place = next(
        (p for p in all_places if
         p["id"].lower() == name.lower() or
         p["name"].lower() == name.lower()), None
    )

    if not place:
        return f"Destination '{name}' not found", 404

    image_path = "/" + place["image"]

    weather = {"temperature": "N/A"}

    safety_info = get_local_safety(place["name"])
    story = ask_ai(f"Give a cultural overview of {place['name']} for a traveler.")
    packing = ask_ai(f"What should someone pack when traveling to {place['name']}?")
    experiences = ask_ai(f"What are unique experiences in {place['name']}?")

    return render_template(
        "destination.html",
        place=place,
        image=image_path,
        weather=weather,
        safety=safety_info,
        story=story,
        packing=packing,
        experiences=experiences
    )


@app.route("/debug/ids")
def debug_ids():
    data = load_json("destinations.json")
    india = [p["id"] for p in data.get("india", [])]
    intl = [p["id"] for p in data.get("international", [])]
    return {"india": india, "international": intl}


@app.route("/api/stays/<place>")
def get_stays(place):
    stays = load_json("stays.json").get(place, [])
    return jsonify(stays)


@app.route("/api/cost", methods=["POST"])
def cost_estimator():
    req = request.json

    destination = req["destination"]
    days = req["days"]
    traveler_type = req["traveler_type"]

    prompt = f"""
    Estimate total budget for a {days}-day trip to {destination}
    for a {traveler_type}. Include:
    - Flights
    - Stay
    - Food
    - Transport
    - Attractions
    - Shopping
    Return only INR values.
    """

    cost = ask_ai(prompt)
    return jsonify({"cost": cost})


@app.route("/api/distance", methods=["POST"])
def distance_api():
    req = request.json
    user_loc = get_user_location()

    place = req["place"]
    coords = ask_ai(f"Give latitude and longitude of {place} as 'lat, lon'")

    try:
        lat, lon = [float(x.strip()) for x in coords.split(",")]
        km = geodesic(
            (user_loc["latitude"], user_loc["longitude"]),
            (lat, lon)
        ).km
        return jsonify({"distance_km": round(km, 2)})
    except:
        return jsonify({"distance_km": "unknown"})


@app.route("/book/<destination>/<stay_name>")
def book_page(destination, stay_name):
    all_stays = load_json("stays.json").get(destination, [])

    stay = next((s for s in all_stays if s["name"] == stay_name), None)

    if stay:
        stay["location"] = destination
        stay["destination"] = destination

    return render_template("booking.html", stay=stay, destination=destination)


@app.route("/api/similar", methods=["POST"])
def similar_stays():
    req = request.json
    dest = req["destination"]

    stays = load_json("stays.json").get(dest, [])

    prompt = (
        f"Recommend 3 alternative stays similar to: "
        f"{[s['name'] for s in stays]}. Return only names."
    )

    ai_list = ask_ai(prompt).split("\n")
    ai_list = [name.strip() for name in ai_list if name.strip()]

    final = [s for s in stays if s["name"] in ai_list]

    if len(final) < 3:
        final = stays[:3]

    for s in final:
        s["location"] = dest

    return jsonify({"stays": final})


# -------------------------------------------------------
# LOGIN
# -------------------------------------------------------
from flask import session

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        users = load_json("users.json")

        for u in users:
            if u["email"] == email and u["password"] == password:
                session["user_id"] = u["id"]
                return redirect("/")

        return "Invalid login", 401

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

from analytics.google_form_metrics import compute_google_form_metrics

@app.route("/api/ux/formdata", methods=["GET"])
def load_google_form_metrics():
    path = "triptide/data/google_form.xlsx"
    metrics = compute_google_form_metrics(path)
    return metrics

# -------------------------------------------------------
# HEALTH CHECK
# -------------------------------------------------------
@app.route("/api/ping")
def ping():
    return jsonify({"status": "alive"})


@app.route("/static/data/<path:filename>")
def serve_data(filename):
    return app.send_static_file(f"data/{filename}")


# -------------------------------------------------------
# START SERVER
# -------------------------------------------------------
if __name__ == "__main__":
    app.run(port=5000, debug=False)
