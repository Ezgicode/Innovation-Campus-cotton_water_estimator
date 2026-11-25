import streamlit as st
import pandas as pd
import numpy as np
import joblib

# ===============================
# MODELİ YÜKLE
# ===============================
model = joblib.load("cotton_et_model.pkl")  # senin eğittiğin model

st.set_page_config(page_title="Cotton Irrigation Decision Support", layout="centered")

st.title("🌱 Daily Cotton Irrigation Calculator")

st.markdown("""
This tool:
- Estimates atmospheric water demand using a **machine learning model**  
- Uses rainfall and a soil factor to estimate **irrigation need**
""")

# ===============================
# ATMOSFER GİRDİLERİ
# ===============================
st.header("🌤️ Weather Data")

temp = st.number_input("Air Temperature (°C)", value=30.0)
rh = st.number_input("Relative Humidity (%)", value=40.0)
rs = st.number_input("Solar Radiation Rs (MJ/m²)", value=25.0)
rn = st.number_input("Net Radiation Rn (MJ/m²)", value=20.0)
wind = st.number_input("Wind Speed (m/s)", value=3.0)
doy = st.number_input("Day of Year (DOY)", min_value=1, max_value=365, value=180)

# ===============================
# SU DENGESİ GİRDİLERİ
# ===============================
st.header("💧 Water Balance")

rain = st.number_input("Today’s Rainfall (mm)", value=0.0)

soil_type = st.selectbox(
    "Soil Type",
    ["Sandy", "Loamy", "Clay"]
)

soil_factor_map = {
    "Sandy": 0.5,
    "Loamy": 1.0,
    "Clay": 1.5
}

soil_factor = soil_factor_map[soil_type]

# ===============================
# HESAPLAMA
# ===============================
if st.button("🔍 Calculate Irrigation"):

    input_df = pd.DataFrame([{
        "NW Air Temp in degrees C": temp,
        "NW RH in %": rh,
        "NW Rs in MJ/m^2": rs,
        "NW Rn in MJ/m^2": rn,
        "NW 2-m Wind Speed in m/s": wind,
        "DOY": doy
    }])

    # MODEL ÇIKTISI
    et_model = model.predict(input_df)[0]

    # NET SU İHTİYACI
    irrigation_need = max(et_model - rain - soil_factor, 0)

    st.success(f"🌬️ Atmospheric Demand (ET): **{et_model:.2f} mm/day**")
    st.info(f"💦 Estimated Irrigation: **{irrigation_need:.2f} mm**")

    if irrigation_need == 0:
        st.write("✅ No irrigation is needed today.")
