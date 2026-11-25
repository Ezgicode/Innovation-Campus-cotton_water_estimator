"""Feature engineering shared by training and the app (model v2)."""
import numpy as np
import pandas as pd
from fao56 import reference_et0, vapour_pressure_deficit

RAW_COLUMNS = {
    "NW Air Temp in degrees C": "temp",
    "NW RH in %": "rh",
    "NW Rs in MJ/m^2": "rs",
    "NW Rn in MJ/m^2": "rn",
    "NW 2-m Wind Speed in m/s": "wind",
}

FEATURES = ["full_irrigation", "et0", "vpd", "temp", "rh", "rs", "rn", "wind", "doy_sin", "doy_cos"]


def build_features(temp, rh, rs, rn, wind, doy, full_irrigation, elevation=1170.0):
    df = pd.DataFrame({
        "temp": np.atleast_1d(temp), "rh": np.atleast_1d(rh), "rs": np.atleast_1d(rs),
        "rn": np.atleast_1d(rn), "wind": np.atleast_1d(wind),
    })
    doy = np.atleast_1d(doy).astype(float)
    df["full_irrigation"] = np.atleast_1d(full_irrigation).astype(int)
    df["et0"] = reference_et0(df.temp, df.rh, df.rn, df.wind, elevation)
    df["vpd"] = vapour_pressure_deficit(df.temp, df.rh)
    df["doy_sin"] = np.sin(2 * np.pi * doy / 365.0)
    df["doy_cos"] = np.cos(2 * np.pi * doy / 365.0)
    return df[FEATURES]
