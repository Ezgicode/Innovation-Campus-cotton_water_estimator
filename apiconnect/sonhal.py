import streamlit as st
import numpy as np
import pandas as pd
import joblib
from datetime import date

from nasa import fetch_nasa_power


# ===============================
# SAYFA AYARLARI + CSS
# ===============================
st.set_page_config(
    page_title="Cotton Water Requirement Estimator",
    layout="centered"
)

st.markdown(
    """
    <style>
    /* Arka plan görseli */
    .stApp {
        background-image: url("https://img.freepik.com/free-photo/fluffy-cotton-plant-with-buds_23-2151104694.jpg?semt=ais_hybrid&w=740&q=80");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }

    /* Üst header tamamen kaldır */
    header {
        visibility: hidden;
        height: 0px;
    }

    /* İçerik paneli */
    .block-container {
        background-color: rgba(255, 255, 255, 0.88);
        padding: 2rem;
        border-radius: 14px;
        margin-top: 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ===============================
# BAŞLIK
# ===============================
st.title("Cotton Water Requirement Estimator")
st.caption("NASA POWER API + ML Model (Ridge)")


# ===============================
# MODELİ YÜKLE
# ===============================
MODEL_PATH = "cotton_et_model2.pkl"
model = joblib.load(MODEL_PATH)


# ===============================
# GİRDİLER
# ===============================
st.subheader("Enter the location and date")

lat = st.number_input("Latitude", value=39.0, format="%.6f")
lon = st.number_input("Longitude", value=35.0, format="%.6f")
selected_date = st.date_input("Date", value=date.today())

st.subheader("Enter irrigation settings")
rain = st.number_input("Today’s rainfall (mm)", value=0.0, min_value=0.0)

eff_map = {
    "Drip (0.90)": 0.90,
    "Sprinkler (0.75)": 0.75,
    "Flood (0.60)": 0.60
}
eff_label = st.selectbox("Irrigation method (efficiency)", list(eff_map.keys()))
eff = eff_map[eff_label]

area = st.number_input("Area (m²)", value=1000.0, min_value=0.0)


# ===============================
# HESAP BUTONU
# ===============================
if st.button("🌍 Fetch NASA data and calculate ET"):
    try:
        with st.spinner("Fetching NASA POWER data..."):
            meteo = fetch_nasa_power(lat, lon, selected_date)

        # NASA -999 TEMİZLİĞİ
        if meteo["rs"] < 0:
            meteo["rs"] = 0.0
        if meteo["rn"] < 0:
            meteo["rn"] = 0.0

        st.success("NASA data retrieved ✅")

        # Tarih özellikleri
        year = selected_date.year
        doy = selected_date.timetuple().tm_yday
        doy_sin = np.sin(2 * np.pi * doy / 365.0)
        doy_cos = np.cos(2 * np.pi * doy / 365.0)

        # MODEL GİRDİSİ
        X_input = pd.DataFrame([{
            "Year": year,
            "NW Air Temp in degrees C": meteo["air_temp"],
            "NW RH in %": meteo["rh"],
            "NW Rs in MJ/m^2": meteo["rs"],
            "NW Rn in MJ/m^2": meteo["rn"],
            "NW 2-m Wind Speed in m/s": meteo["wind"],
            "DOY_sin": doy_sin,
            "DOY_cos": doy_cos
        }])

        # Tahmin
        ET = float(model.predict(X_input)[0])

        # SULAMA HESABI
        net_irrigation = max(ET - rain, 0.0)
        gross_irrigation = net_irrigation / eff if eff > 0 else 0.0
        liters = gross_irrigation * area

        st.subheader("Results")
        col1, col2, col3 = st.columns(3)
        col1.metric("ET (mm/day)", f"{ET:.2f}")
        col2.metric("Net irrigation (mm)", f"{net_irrigation:.2f}")
        col3.metric("Gross irrigation (mm)", f"{gross_irrigation:.2f}")

        st.metric("Total water (liters)", f"{liters:.0f}")

        st.subheader("🌤 NASA Weather Data")
        st.json({
            "Air Temperature (°C)": meteo["air_temp"],
            "Relative Humidity (%)": meteo["rh"],
            "Wind Speed (m/s)": meteo["wind"],
            "Solar Radiation Rs (MJ/m²)": meteo["rs"],
            "Net Radiation Rn (MJ/m²)": meteo["rn"]
        })

    except Exception as e:
        st.error(str(e))
