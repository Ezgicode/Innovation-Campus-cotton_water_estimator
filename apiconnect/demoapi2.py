import streamlit as st
import numpy as np
import pandas as pd
import joblib
from datetime import date

from nasa import fetch_nasa_power



# ===============================
# SAYFA
# ===============================
st.set_page_config(page_title="Cotton Water Requirement Estimator", layout="centered")

st.title(" Cotton Water Requirement Estimator")
st.caption("NASA POWER API + ML Model (Ridge)")

# ===============================
# MODELİ YÜKLE
# ===============================
MODEL_PATH = "cotton_et_model2.pkl"
model = joblib.load(MODEL_PATH)

# ===============================
# GİRDİLER
# ===============================
st.subheader("Lütfen konum ve tarih bilgilerini giriniz")

lat = st.number_input("Latitude", value=39.0, format="%.6f")
lon = st.number_input("Longitude", value=35.0, format="%.6f")
selected_date = st.date_input("Date", value=date.today())

st.subheader("Lütfen sulama ayarlarını giriniz")
rain = st.number_input("Bugünkü yağış (mm)", value=0.0, min_value=0.0)

eff_map = {
    "Damla (0.90)": 0.90,
    "Yağmurlama (0.75)": 0.75,
    "Salma (0.60)": 0.60
}
eff_label = st.selectbox("Sulama yöntemi (verim)", list(eff_map.keys()))
eff = eff_map[eff_label]

area = st.number_input("Alan (m²)", value=1000.0, min_value=0.0)

# ===============================
# HESAP BUTONU
# ===============================
if st.button("🌍 NASA’dan veriyi çek + ET hesapla"):
    try:
        with st.spinner("NASA POWER verisi çekiliyor..."):
            meteo = fetch_nasa_power(lat, lon, selected_date)
        # ===============================
        # NASA -999 TEMİZLİĞİ
        # ===============================
        if meteo["rs"] < 0:
            meteo["rs"] = 0.0

        if meteo["rn"] < 0:
            meteo["rn"] = 0.0

        st.success("NASA verisi alındı ✅")

        # Tarih özellikleri
        year = selected_date.year
        doy = selected_date.timetuple().tm_yday
        doy_sin = np.sin(2 * np.pi * doy / 365.0)
        doy_cos = np.cos(2 * np.pi * doy / 365.0)

        # ===============================
        # MODEL GİRDİSİ (DİKKAT: Year VAR, Year_norm YOK)
        # ===============================
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
        # NASA bazen -999 döndürür → fiziksel olmayan değer


        # Tahmin
        ET = float(model.predict(X_input)[0])

        # ===============================
        # SULAMA HESABI (basit)
        # Net = max(ET - yağış, 0)
        # Gross = Net / verim
        # 1 mm = 1 L / m²
        # ===============================
        net_irrigation = max(ET - rain, 0.0)
        gross_irrigation = net_irrigation / eff if eff > 0 else 0.0
        liters = gross_irrigation * area

        st.subheader("        Sonuçlar")
        col1, col2, col3 = st.columns(3)
        col1.metric("ET (mm/gün)", f"{ET:.2f}")
        col2.metric("Net sulama (mm)", f"{net_irrigation:.2f}")
        col3.metric("Verilecek su (mm)", f"{gross_irrigation:.2f}")

        st.metric("Toplam su (litre)", f"{liters:.0f}")

        st.subheader("🌤 NASA Meteorolojik Veriler")

        st.json({
            "Air Temperature (°C)": meteo["air_temp"],
            "Relative Humidity (%)": meteo["rh"],
            "Wind Speed (m/s)": meteo["wind"],
            "Solar Radiation Rs (MJ/m²)": meteo["rs"],
            "Net Radiation Rn (MJ/m²)": meteo["rn"]
        })



    except Exception as e:
        st.error(str(e))
