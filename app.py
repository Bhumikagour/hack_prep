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

AMBULANCES = pd.DataFrame([
    {"unit": "KA-01-A", "area": "Indiranagar",  "lat": 12.9719, "lon": 77.6412, "crew": "ALS", "status": "Available"},
    {"unit": "KA-01-B", "area": "Jayanagar",    "lat": 12.9250, "lon": 77.5938, "crew": "BLS", "status": "Available"},
    {"unit": "KA-01-C", "area": "Whitefield",   "lat": 12.9698, "lon": 77.7500, "crew": "ALS", "status": "On call"},
    {"unit": "KA-01-D", "area": "Hebbal",       "lat": 13.0358, "lon": 77.5970, "crew": "ALS", "status": "Available"},
    {"unit": "KA-01-E", "area": "Koramangala",  "lat": 12.9352, "lon": 77.6245, "crew": "BLS", "status": "Available"},
])

# --- HEADER ----------------------------------------------------------------
st.title("Dispatch")
st.caption("BBMP Emergency Control Room  ·  Dispatcher: Priya Menon  ·  synthetic data")

free = (AMBULANCES.status == "Available").sum()
c1, c2, c3 = st.columns(3)
c1.metric("Ambulances available", f"{free} of {len(AMBULANCES)}")
c2.metric("ICU beds citywide", int(HOSPITALS.icu_free.sum()))
c3.metric("ERs at high load", int((HOSPITALS.er_load == "High").sum()))

st.divider()

# --- MAP -------------------------------------------------------------------
h = HOSPITALS[["lat", "lon"]].copy()
h["color"], h["size"] = "#2F6F4F", 260

a = AMBULANCES[["lat", "lon"]].copy()
a["color"], a["size"] = "#C0392A", 170

st.map(pd.concat([h, a], ignore_index=True), color="color", size="size", zoom=11)

st.subheader("Hospital capacity")
st.dataframe(HOSPITALS, use_container_width=True, hide_index=True)