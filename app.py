import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dispatch", page_icon="🚑", layout="wide")

# --- SEEDED DATA (synthetic; real hospitals, invented capacity) -------------
HOSPITALS = pd.DataFrame([
    {"name": "Victoria Hospital",        "lat": 12.9634, "lon": 77.5747, "icu_free": 3, "specialties": "Trauma, Cardiac, General", "o_neg": 6, "trauma_level": 1, "er_load": "High"},
    {"name": "St. John's Medical",       "lat": 12.9279, "lon": 77.6218, "icu_free": 5, "specialties": "Trauma, Neuro, General",   "o_neg": 4, "trauma_level": 1, "er_load": "Medium"},
    {"name": "Manipal Old Airport Rd",   "lat": 12.9581, "lon": 77.6486, "icu_free": 2, "specialties": "Cardiac, Neuro",          "o_neg": 2, "trauma_level": 2, "er_load": "High"},
    {"name": "Sakra World, Marathahalli","lat": 12.9345, "lon": 77.6974, "icu_free": 8, "specialties": "Cardiac, Neuro, Ortho",   "o_neg": 9, "trauma_level": 2, "er_load": "Low"},
    {"name": "Sparsh, Yeshwanthpur",     "lat": 13.0221, "lon": 77.5497, "icu_free": 4, "specialties": "Ortho, Trauma",           "o_neg": 0, "trauma_level": 2, "er_load": "Medium"},
    {"name": "Vydehi, Whitefield",       "lat": 12.9784, "lon": 77.7276, "icu_free": 6, "specialties": "General, Ortho",          "o_neg": 3, "trauma_level": 3, "er_load": "Low"},
    {"name": "Jayadeva Cardiology",      "lat": 12.9166, "lon": 77.5993, "icu_free": 7, "specialties": "Cardiac",                 "o_neg": 5, "trauma_level": 3, "er_load": "Medium"},
    {"name": "Bowring & Lady Curzon",    "lat": 12.9827, "lon": 77.6041, "icu_free": 1, "specialties": "General",                 "o_neg": 1, "trauma_level": 3, "er_load": "High"},
])

from math import radians, sin, cos, asin, sqrt

SCENES = {
    "Hebbal Flyover":          (13.0358, 77.5912),
    "Silk Board Junction":     (12.9172, 77.6229),
    "Marathahalli Bridge":     (12.9560, 77.7010),
    "Majestic Bus Station":    (12.9767, 77.5713),
    "Electronic City Phase 1": (12.8452, 77.6602),
    "Indiranagar 100ft Road":  (12.9719, 77.6412),
}

AVG_SPEED_KMPH = 22   # siren-assisted average through Bengaluru traffic

def km_between(a, b):
    (lat1, lon1), (lat2, lon2) = a, b
    dlat, dlon = radians(lat2 - lat1), radians(lon2 - lon1)
    x = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return 2 * 6371 * asin(sqrt(x))

def assess(h, scene, condition, severity, needs_o_neg):
    """Score one hospital for one incident. Returns score, ETA, reasons, blockers."""
    eta = round(km_between(scene, (h.lat, h.lon)) / AVG_SPEED_KMPH * 60)
    score, why, blockers = 100.0, [f"{eta} min out"], []

    score -= min(eta * 1.2, 45)

    if condition in h.specialties:
        why.append(f"{condition} unit on site")
    else:
        score -= 30
        why.append(f"no {condition} unit")

    if severity == "Critical":
        if h.icu_free == 0:
            blockers.append("no ICU bed")
        else:
            score += min(h.icu_free, 5) * 2
            why.append(f"{h.icu_free} ICU free")

    if needs_o_neg:
        if h.o_neg == 0:
            blockers.append("no O\u2212 in bank")
        else:
            why.append(f"O\u2212 \u00d7{h.o_neg}")

    score -= {"High": 12, "Medium": 5, "Low": 0}[h.er_load]
    if h.er_load == "High":
        why.append("ER at high load")

    if condition == "Trauma":
        score += {1: 10, 2: 0, 3: -10}[h.trauma_level]
        if h.trauma_level == 1:
            why.append("Level 1 trauma centre")

    if blockers:
        score = min(score, 15)
    return round(max(score, 0)), eta, " \u00b7 ".join(why), ", ".join(blockers)

# --- HEADER ----------------------------------------------------------------
st.title("Dispatch")
st.caption("BBMP Emergency Control Room  ·  Dispatcher: Priya Menon  ·  synthetic data")

left, right = st.columns([1, 2], gap="large")

with left:
    st.subheader("Incoming call")
    with st.form("incident"):
        scene_name  = st.selectbox("Scene", list(SCENES))
        condition   = st.selectbox("Presenting condition",
                                   ["Trauma", "Cardiac", "Neuro", "Ortho", "General"])
        severity    = st.radio("Severity", ["Critical", "Serious", "Stable"], horizontal=True)
        needs_o_neg = st.checkbox("O\u2212 blood required")
        st.form_submit_button("Find receiving hospital", type="primary",
                              use_container_width=True)

scene = SCENES[scene_name]

# nearest available ambulance
avail = AMBULANCES[AMBULANCES.status == "Available"].copy()
avail["km"] = [round(km_between(scene, (r.lat, r.lon)), 1) for r in avail.itertuples()]
amb = avail.sort_values("km").iloc[0]

with left:
    st.metric("Nearest unit", amb.unit, f"{amb.km} km · {amb.crew} crew", delta_color="off")

# rank every hospital
rows = []
for h in HOSPITALS.itertuples():
    s, eta, why, blocked = assess(h, scene, condition, severity, needs_o_neg)
    rows.append({"Hospital": h.name, "Score": s, "ETA": eta,
                 "Assessment": why, "Blocked": blocked})
ranked = pd.DataFrame(rows).sort_values("Score", ascending=False).reset_index(drop=True)
best = ranked.iloc[0]

with right:
    st.subheader("Recommended receiving hospital")
    if best.Blocked:
        st.error(f"No hospital clears every requirement. Closest option "
                 f"**{best.Hospital}** is blocked: {best.Blocked}.")
    else:
        st.success(f"**{best.Hospital}** — {best.Assessment}")

    st.dataframe(
        ranked, use_container_width=True, hide_index=True,
        column_config={
            "Score": st.column_config.ProgressColumn("Suitability", min_value=0,
                                                     max_value=120, format="%d"),
            "ETA": st.column_config.NumberColumn("ETA", format="%d min"),
        },
    )

    pts = HOSPITALS[["lat", "lon"]].copy()
    pts["color"] = ["#2F6F4F" if h.name == best.Hospital else "#B9B1A8"
                    for h in HOSPITALS.itertuples()]
    pts["size"] = [320 if h.name == best.Hospital else 180
                   for h in HOSPITALS.itertuples()]
    pts.loc[len(pts)] = [scene[0], scene[1], "#C0392A", 400]
    st.map(pts, color="color", size="size", zoom=11)