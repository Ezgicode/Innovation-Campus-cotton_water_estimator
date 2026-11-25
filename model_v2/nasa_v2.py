"""NASA POWER helper for model v2.

Differences from apiconnect/nasa.py (left untouched):
  * tries the selected date first, then up to 7 days earlier,
  * returns the date that was actually used and the site elevation.
"""
from datetime import date, timedelta

import requests

BASE_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"


def fetch_nasa_power(lat: float, lon: float, selected_date: date) -> dict:
    for i in range(0, 8):
        d = selected_date - timedelta(days=i)
        ds = d.strftime("%Y%m%d")
        url = (f"{BASE_URL}?parameters=T2M,RH2M,WS2M,ALLSKY_SFC_SW_DWN&community=AG"
               f"&longitude={lon}&latitude={lat}&start={ds}&end={ds}&format=JSON")
        try:
            r = requests.get(url, timeout=15)
            r.raise_for_status()
            data = r.json()
            p = data["properties"]["parameter"]
            values = [p["T2M"][ds], p["RH2M"][ds], p["WS2M"][ds], p["ALLSKY_SFC_SW_DWN"][ds]]
            if any(v is None or v <= -990 for v in values):
                continue  # NASA uses -999 for missing values
            temp, rh, wind, rs = map(float, values)
            coords = data.get("geometry", {}).get("coordinates", [])
            elevation = float(coords[2]) if len(coords) > 2 else 0.0
            return {"date_used": d.isoformat(), "air_temp": temp, "rh": rh, "wind": wind,
                    "rs": rs, "rn": 0.75 * rs, "elevation": elevation}
        except Exception:
            continue
    raise RuntimeError("NASA POWER: no complete data found for the selected date or the previous seven days.")
