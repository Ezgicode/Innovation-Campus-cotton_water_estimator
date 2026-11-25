import streamlit as st
import numpy as np
import joblib
import datetime

# ===============================
# MODELİ YÜKLE
# ===============================
model = joblib.load("cotton_et_model.pkl")

st.set_page_config(page_title="Cotton ET Estimator", layout="centered")

st.title("🌱 Cotton Water Requirement Estimator")
st.markdown("Estimate **daily evapotranspiration (ET)** for cotton fields.")

# ===============================
# KULLANICI GİRDİLERİ
# ===============================
st.header("📥 Input Data")

temp = st.number_input("Air Temperature (°C)", value=25.0)
rh = st.number_input("Relative Humidity (%)", value=50.0)
rs = st.number_input("Solar Radiation Rs (MJ/m²)", value=20.0)
rn = st.number_input("Net Radiation Rn (MJ/m²)", value=15.0)
wind = st.number_input("Wind Speed (m/s)", value=3.0)

date = st.date_input("Date", datetime.date.today())
doy = date.timetuple().tm_yday
year = date.year

# ===============================
# MEVSİMSEL DÖNÜŞÜM
# ===============================
sin_doy = np.sin(2 * np.pi * doy / 365)
cos_doy = np.cos(2 * np.pi * doy / 365)

# ⚠️ Year normalization (eğitimde kullandığın ortalama/std ile)
YEAR_MEAN = 2006.5   # burayı eğitimdeki değerle değiştir
YEAR_STD = 7.8

year_norm = (year - YEAR_MEAN) / YEAR_STD

# ===============================
# TAHMİN
# ===============================
if st.button("🚀 Calculate ET"):
    X = np.array([[temp, rh, rs, rn, wind, sin_doy, cos_doy, year_norm]])
    et = model.predict(X)[0]

    st.success(f"🌊 Estimated ET: **{et:.2f} mm/day**")

    st.info(
        "This value represents **atmospheric evaporative demand**.\n\n"
        "Crop water requirement (ETc) can be calculated using:\n"
        "**ETc = ET × Kc**"
    )
