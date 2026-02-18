import json
import os
from datetime import datetime
from collections import defaultdict

ANALYTICS_DIR = "analytics"
DATA_FILE = os.path.join(ANALYTICS_DIR, "analytics_data.json")
os.makedirs(ANALYTICS_DIR, exist_ok=True)


# ----------------------------
# Helpers
# ----------------------------
def load_analytics():
    if not os.path.exists(DATA_FILE):
        return {
            "metrics": {},
            "sus_scores": [],
            "nps_scores": [],
            "ctr": {},
        }

    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {
            "metrics": {},
            "sus_scores": [],
            "nps_scores": [],
            "ctr": {},
        }


def save_analytics(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


def ensure_user(data, user):
    if user not in data["metrics"]:
        data["metrics"][user] = {
            "page_visits": defaultdict(int),
            "click_events": defaultdict(int),
            "load_times": defaultdict(list),
            "scroll_depth": defaultdict(list),
            "ai_usage": {"local": 0, "online": 0},
            "tasks": {
                "attempt": defaultdict(int),
                "success": defaultdict(int),
                "error": defaultdict(int),
                "duration": defaultdict(list),
            },
        }


# ----------------------------
# Logging functions
# ----------------------------
def log_page(user, page):
    data = load_analytics()
    ensure_user(data, user)
    data["metrics"][user]["page_visits"][page] += 1
    save_analytics(data)


def log_click(user, event):
    data = load_analytics()
    ensure_user(data, user)
    data["metrics"][user]["click_events"][event] += 1
    save_analytics(data)


def log_load_time(user, page, t):
    data = load_analytics()
    ensure_user(data, user)

    # Ensure nested dict exists
    if page not in data["metrics"][user]["load_times"]:
        data["metrics"][user]["load_times"][page] = []

    data["metrics"][user]["load_times"][page].append(t)
    save_analytics(data)



def log_scroll(user, page, depth):
    data = load_analytics()
    ensure_user(data, user)

    if page not in data["metrics"][user]["scroll_depth"]:
        data["metrics"][user]["scroll_depth"][page] = []

    data["metrics"][user]["scroll_depth"][page].append(depth)
    save_analytics(data)


def log_ai(user, source):
    data = load_analytics()
    ensure_user(data, user)
    data["metrics"][user]["ai_usage"][source] += 1
    save_analytics(data)


def log_task_attempt(user, task):
    data = load_analytics()
    ensure_user(data, user)
    data["metrics"][user]["tasks"]["attempt"][task] += 1
    save_analytics(data)


def log_task_success(user, task, dur):
    data = load_analytics()
    ensure_user(data, user)
    data["metrics"][user]["tasks"]["success"][task] += 1
    data["metrics"][user]["tasks"]["duration"][task].append(dur)
    save_analytics(data)


def log_task_error(user, task):
    data = load_analytics()
    ensure_user(data, user)
    data["metrics"][user]["tasks"]["error"][task] += 1
    save_analytics(data)


# ----------------------------
# SUS & NPS
# ----------------------------
def calculate_sus(answers):
    total = 0
    for i, a in enumerate(answers):
        total += (a - 1) if (i % 2 == 0) else (5 - a)
    return round(total * 2.5, 2)


def submit_sus(user, answers):
    score = calculate_sus(answers)
    data = load_analytics()
    data["sus_scores"].append(score)
    save_analytics(data)
    return score


def submit_nps(user, score):
    data = load_analytics()
    data["nps_scores"].append(score)
    save_analytics(data)


# ----------------------------
# Derived Metrics
# ----------------------------
def compute_tsr(u):
    a = sum(u["tasks"]["attempt"].values())
    s = sum(u["tasks"]["success"].values())
    return round((s / a) * 100, 2) if a else 0


def compute_uer(u):
    a = sum(u["tasks"]["attempt"].values())
    e = sum(u["tasks"]["error"].values())
    return round((e / a) * 100, 2) if a else 0


# ----------------------------
# Final Metric Calculation
# ----------------------------

import re
import json
from collections import defaultdict

def compute_metrics():
    data = load_analytics()

    total_visits = defaultdict(int)
    total_clicks = defaultdict(int)
    ai = {"local": 0, "online": 0}
    load_avg = {}
    scroll_avg = {}

    for u, m in data["metrics"].items():

        for p, c in m["page_visits"].items():
            total_visits[p] += c

        for e, c in m["click_events"].items():
            total_clicks[e] += c

        for src, cnt in m["ai_usage"].items():
            ai[src] += cnt

        for p, t in m["load_times"].items():
            if t:
                load_avg[p] = sum(t) / len(t)

        for p, d in m["scroll_depth"].items():
            if d:
                scroll_avg[p] = sum(d) / len(d)


    # --------------- HARD-CODED UX METRICS FROM GOOGLE FORM --------------------
    UX = {
        "sus": 83.3,
        "nps": 60.8,
        "tsr": 93.47,
        "uer": 27.53,
        "engagement": 4.43,
        "ctr": 0.88,
        "retention": 4.34,
        "difficulty": 3.91
    }
    # ---------------------------------------------------------------------------

    return {
        "page_visits": dict(total_visits),
        "click_events": dict(total_clicks),
        "ai_usage": ai,
        "page_load_times": load_avg,
        "scroll_depth": scroll_avg,

        # FLATTENED UX METRICS (admin.html expects these directly)
        "sus": UX["sus"],
        "nps": UX["nps"],
        "tsr": UX["tsr"],
        "uer": UX["uer"],
        "engagement": UX["engagement"],
        "retention": UX["retention"],
        "difficulty": UX["difficulty"],
        "ctr": UX["ctr"]
    }
