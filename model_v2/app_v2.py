"""Cotton Water Requirement Estimator - v2.

Run from this folder:  streamlit run app_v2.py
The original apps in ../apiconnect and ../demoweb are unchanged.
"""
import json
from datetime import date
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import streamlit as st

from features import build_features
from nasa_v2 import fetch_nasa_power

HERE = Path(__file__).resolve().parent

st.set_page_config(page_title="Cotton Water Requirement Estimator v2", layout="centered")
st.markdown("""
<style>
.stApp {background-image: url("https://img.freepik.com/free-photo/fluffy-cotton-plant-with-buds_23-2151104694.jpg?semt=ais_hybrid&w=740&q=80");
        background-size: cover; background-position: center;}
header {visibility: hidden; height: 0px;}
.block-container {background-color: rgba(255,255,255,0.90); padding: 2rem; border-radius: 14px; margin-top: 0;}
</style>""", unsafe_allow_html=True)


@st.cache_resource
def load_model():
    try:
        return joblib.load(HERE / "cotton_et_model_v2.pkl")
    except Exception:
        # e.g. a different scikit-learn version: retrain from the original data (takes a few seconds)
        import train_v2
        train_v2.main()
        return joblib.load(HERE / "cotton_et_model_v2.pkl")


@st.cache_resource
def load_v1():
    try:
        return joblib.load(HERE.parent / "apiconnect" / "cotton_et_model2.pkl")
    except Exception:
        return None


model = load_model()

st.title("Cotton Water Requirement Estimator")
st.caption("v2 · NASA POWER + FAO-56 Penman-Monteith + Random Forest")

metrics_file = HERE / "results" / "metrics_v1_vs_v2.json"
if metrics_file.exists():
    m = json.loads(metrics_file.read_text())
    a, b = m["v1"]["test_split_80_20"], m["v2"]["test_split_80_20"]
    st.info(f"Test error: MAE {a['MAE']:.2f} → **{b['MAE']:.2f} mm/day**, R² {a['R2']:.2f} → **{b['R2']:.2f}** (v1 → v2)")

st.subheader("Location and date")
c1, c2 = st.columns(2)
lat = c1.number_input("Latitude", value=37.159, format="%.4f")
lon = c2.number_input("Longitude", value=39.004, format="%.4f")
selected_date = st.date_input("Date", value=date.today())

st.subheader("Field and irrigation")
regime = st.radio("Water regime", ["Full irrigation (well-watered)", "Limited / deficit irrigation"], horizontal=True)
rain = st.number_input("Today's rainfall (mm)", value=0.0, min_value=0.0)
eff_map = {"Drip (0.90)": 0.90, "Sprinkler (0.75)": 0.75, "Flood (0.60)": 0.60}
eff_label = st.selectbox("Irrigation method (efficiency)", list(eff_map))
area = st.number_input("Area (m²)", value=10000.0, min_value=0.0)

if st.button("🌍 Fetch NASA data and estimate water need"):
    try:
        with st.spinner("Fetching NASA POWER data..."):
            w = fetch_nasa_power(lat, lon, selected_date)
        used = date.fromisoformat(w["date_used"])
        doy = used.timetuple().tm_yday
        full = regime.startswith("Full")
        x = build_features(w["air_temp"], w["rh"], w["rs"], w["rn"], w["wind"], doy, full, w["elevation"])
        et0 = float(x["et0"].iloc[0])
        etc = float(model.predict(x)[0])
        net = max(etc - rain, 0.0)
        gross = net / eff_map[eff_label]
        liters = gross * area

        st.success(f"NASA data retrieved for {w['date_used']} (elevation {w['elevation']:.0f} m) ✅")
        st.subheader("Results")
        r1, r2, r3 = st.columns(3)
        r1.metric("Reference ET₀ (mm/day)", f"{et0:.2f}")
        r2.metric("Cotton ET (mm/day)", f"{etc:.2f}")
        r3.metric("Crop coefficient (ET/ET₀)", f"{etc / et0:.2f}" if et0 > 0 else "–")
        r4, r5, r6 = st.columns(3)
        r4.metric("Net irrigation (mm)", f"{net:.2f}")
        r5.metric("Gross irrigation (mm)", f"{gross:.2f}")
        r6.metric("Total water (liters)", f"{liters:,.0f}")

        with st.expander("🌤 NASA weather data"):
            st.json({k: round(v, 2) if isinstance(v, float) else v for k, v in w.items()})

        v1 = load_v1()
        if v1 is not None:
            x1 = pd.DataFrame([{
                "Year": used.year, "NW Air Temp in degrees C": w["air_temp"], "NW RH in %": w["rh"],
                "NW Rs in MJ/m^2": w["rs"], "NW Rn in MJ/m^2": w["rn"], "NW 2-m Wind Speed in m/s": w["wind"],
                "DOY_sin": np.sin(2 * np.pi * doy / 365), "DOY_cos": np.cos(2 * np.pi * doy / 365)}])
            with st.expander("Compare with v1 model"):
                st.write(f"v1 (Ridge with Year) predicts **{float(v1.predict(x1)[0]):.2f} mm/day** for the same weather. "
                         "v1 uses the year as a feature, so for years after 2012 it extrapolates upwards.")
        st.caption("Exploratory decision-support prototype trained on Bushland, Texas lysimeter data (2000-2012); not a validated field recommendation.")
    except Exception as e:
        st.error(str(e))
