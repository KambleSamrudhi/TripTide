import pandas as pd
import json

def map_nps_scale(x):
    mapping = {1: 2, 2: 4, 3: 6, 4: 8, 5: 10}
    return mapping.get(x, 0)

def compute_google_form_metrics(path):
    df = pd.read_excel(path)

    results = {}

    # ---------------------------
    # 1. TSR – Task Success Rate
    # ---------------------------
    tsr_map = {"Yes": 1, "Partially": 0.5, "No": 0}
    tsr_col = df["Were you able to complete the assigned tasks?"]
    tsr_scores = tsr_col.map(tsr_map)
    results["tsr"] = round(tsr_scores.mean() * 100, 2)

    # ---------------------------
    # 2. UER – User Error Rate
    # ---------------------------
    err_map = {"<2": 1, "<5": 3, ">5": 6}
    errors = df["How many errors/difficulties did you face?"].map(err_map)
    max_actions = len(df) * 6
    results["uer"] = round((errors.sum() / max_actions) * 100, 2)

    # ---------------------------
    # 3. Difficulty Score
    # ---------------------------
    results["difficulty"] = df["Rate the difficulty of completing the tasks."].mean()

    # ---------------------------
    # 4. SUS – 10 item scale
    # ---------------------------
    sus_cols = [
        "I think that I would like to use this system frequently.",
        "I found the system unnecessarily complex.",
        "I thought the system was easy to use.",
        "I think that I would need help from a technical person.",
        "I found the various functions in this system were well integrated.",
        "I thought there was too much inconsistency in this system.",
        "I imagine most people would learn to use this system very quickly.",
        "I found the system very cumbersome to use.",
        "I felt very confident using the system.",
        "I needed to learn a lot of things before I could get going.",
    ]

    sus_raw = df[sus_cols].astype(int)
    sus_scores = []

    for _, row in sus_raw.iterrows():
        score = 0
        for i, v in enumerate(row):
            if (i + 1) % 2 == 1:
                score += (v - 1)
            else:
                score += (5 - v)
        sus_scores.append(score * 2.5)

    results["sus"] = round(sum(sus_scores) / len(sus_scores), 2)

    # ---------------------------
    # 5. Engagement
    # ---------------------------
    results["engagement"] = df["How engaging did you find the system?"].mean()

    # ---------------------------
    # 6. CTR
    # ---------------------------
    ctr_map = {"Yes": 1, "Sometimes": 0.5, "Rarely": 0.2, "No": 0}
    results["ctr"] = df["Did you click on recommended features when suggested (CTR)?"].map(ctr_map).mean()

    # ---------------------------
    # 7. Retention Intent
    # ---------------------------
    results["retention"] = df["How likely are you to return to this tool for future trips?"].mean()

    # ---------------------------
    # 8. NPS
    # ---------------------------
    nps_raw = df["How likely are you to recommend this system to a friend or colleague?"].astype(int)
    nps_scores = nps_raw.map(map_nps_scale)

    promoters = (nps_scores >= 9).sum()
    detractors = (nps_scores <= 6).sum()
    total = len(nps_scores)

    results["nps"] = round(((promoters - detractors) / total) * 100, 2)

    # ---------------------------
    # 9. Feature Usage
    # ---------------------------
    feature_cols = "Which features did you use? (Select all that apply)"
    usage_counts = {}

    for row in df[feature_cols].dropna():
        for feature in str(row).split(","):
            feature = feature.strip()
            if feature not in usage_counts:
                usage_counts[feature] = 0
            usage_counts[feature] += 1

    results["feature_usage"] = usage_counts

    return results
