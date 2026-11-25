import streamlit as st
import requests
import numpy as np
import pandas as pd
import joblib
from datetime import date


# ===============================
# MODEL YÜKLE
# ===============================
model = joblib.load("cotton_et_model.pkl")

# ===============================
# NASA POWER API FONKSİYONU
# ===============================
def fetch_nasa_power(lat, lon, d):
    url = (
        "https://power.larc.nasa.gov/api/temporal/daily/point"
        "?parameters=T2M,RH2M,ALLSKY_SFC_SW_DWN,ALLSKY_SFC_LW_DWN,WS2M"
        f"&community=AG&longitude={lon}&latitude={lat}"
        f"&start={d}&end={d}&format=JSON"
    )

    r = requests.get(url, timeout=15)
    data = r.json()

    if "properties" not in data:
        raise ValueError("NASA POWER veri döndürmedi")

    p = data["properties"]["parameter"]

    return {
        "temp": p["T2M"][d],
        "rh": p["RH2M"][d],
        "rs": p["ALLSKY_SFC_SW_DWN"][d],   # MJ/m²
        "rn": p["ALLSKY_SFC_LW_DWN"][d],   # MJ/m² (yaklaşım)
        "wind": p["WS2M"][d]
    }

# ===============================
# STREAMLIT UI
# ===============================
st.set_page_config(page_title="Pamuk Sulama Asistanı", layout="centered")

st.title("🌱 Pamuk Sulama Karar Destek Sistemi")
st.caption("ML + FAO mantığı ile günlük sulama ihtiyacı")

lat = st.number_input("Enlem", value=39.0)
lon = st.number_input("Boylam", value=35.0)
selected_date = st.date_input("Tarih", max_value=date.today())

soil_factor = st.selectbox(
    "Toprak tipi",
    {
        "Kumlu": 1.15,
        "Tınlı": 1.00,
        "Killi": 0.85
    }.keys()
)

rain_mm = st.number_input("Bugün düşen yağış (mm)", value=0.0)

if st.button("Hesapla"):
    try:
        d_str = selected_date.strftime("%Y%m%d")
        doy = selected_date.timetuple().tm_yday

        meteo = fetch_nasa_power(lat, lon, d_str)

        # ===============================
        # FEATURE HAZIRLA
        # ===============================
        X = pd.DataFrame([{
            "NW Air Temp in degrees C": meteo["temp"],
            "NW RH in %": meteo["rh"],
            "NW Rs in MJ/m^2": meteo["rs"],
            "NW Rn in MJ/m^2": meteo["rn"],
            "NW 2-m Wind Speed in m/s": meteo["wind"],
            "DOY_sin": np.sin(2 * np.pi * doy / 365),
            "DOY_cos": np.cos(2 * np.pi * doy / 365),
        }])

        # ===============================
        # MODEL TAHMİNİ (ET)
        # ===============================
        et_mm = float(model.predict(X)[0])

        # ===============================
        # SULAMA HESABI (BASİT AMA DOĞRU)
        # ===============================
        soil_coeff = {
            "Kumlu": 1.15,
            "Tınlı": 1.00,
            "Killi": 0.85
        }[soil_factor]

        irrigation_mm = max(et_mm * soil_coeff - rain_mm, 0)

        # ===============================
        # SONUÇ
        # ===============================
        st.success("Hesaplama tamamlandı")

        st.metric("🌬 Atmosferin çektiği su (ET)", f"{et_mm:.2f} mm/gün")
        st.metric("🚿 Önerilen sulama", f"{irrigation_mm:.2f} mm")

    except Exception as e:
        st.error(f"Hata: {e}")
