import requests
from datetime import date, timedelta


def fetch_nasa_power(lat: float, lon: float, selected_date: date) -> dict:
    """
    NASA POWER DAILY API
    Son 7 günü dener, veri olan ilk günü alır.
    """

    base_url = "https://power.larc.nasa.gov/api/temporal/daily/point"

    for i in range(1, 8):  # son 7 günü dene
        d = selected_date - timedelta(days=i)
        date_str = d.strftime("%Y%m%d")

        url = (
            f"{base_url}"
            "?parameters=T2M,RH2M,WS2M,ALLSKY_SFC_SW_DWN"
            "&community=AG"
            f"&longitude={lon}"
            f"&latitude={lat}"
            f"&start={date_str}"
            f"&end={date_str}"
            "&format=JSON"
        )

        try:
            r = requests.get(url, timeout=15)
            r.raise_for_status()
            data = r.json()

            params = data["properties"]["parameter"]

            air_temp = params["T2M"][date_str]
            rh = params["RH2M"][date_str]
            wind = params["WS2M"][date_str]
            rs = params["ALLSKY_SFC_SW_DWN"][date_str]

            # Net radiation YOK → approx hesap
            rn = rs * 0.75   # FAO pratik yaklaşım

            return {
                "date_used": d.isoformat(),
                "air_temp": float(air_temp),
                "rh": float(rh),
                "wind": float(wind),
                "rs": float(rs),
                "rn": float(rn),
            }

        except Exception:
            continue

    raise RuntimeError("NASA POWER: No data was found for the previous seven days.")
