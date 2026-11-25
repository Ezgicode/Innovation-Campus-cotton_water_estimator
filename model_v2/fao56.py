"""FAO-56 Penman-Monteith helpers (Allen et al., 1998) for daily data."""
import numpy as np


def saturation_vp(t):
    """Saturation vapour pressure (kPa) at air temperature t (degC)."""
    return 0.6108 * np.exp(17.27 * t / (t + 237.3))


def reference_et0(t, rh, rn, u2, elevation=1170.0, g=0.0):
    """Daily grass reference evapotranspiration ET0 (mm/day).

    t: mean air temperature (degC), rh: relative humidity (%),
    rn: net radiation (MJ/m2/day), u2: wind speed at 2 m (m/s),
    elevation: site elevation (m), g: soil heat flux (~0 for daily steps).
    """
    t, rh, rn, u2 = (np.asarray(v, dtype=float) for v in (t, rh, rn, u2))
    pressure = 101.3 * ((293 - 0.0065 * elevation) / 293) ** 5.26
    gamma = 0.000665 * pressure
    es = saturation_vp(t)
    ea = es * rh / 100.0
    delta = 4098 * es / (t + 237.3) ** 2
    num = 0.408 * delta * (rn - g) + gamma * (900 / (t + 273)) * u2 * (es - ea)
    den = delta + gamma * (1 + 0.34 * u2)
    return np.clip(num / den, 0, None)


def vapour_pressure_deficit(t, rh):
    """Vapour pressure deficit (kPa)."""
    return saturation_vp(np.asarray(t, float)) * (1 - np.asarray(rh, float) / 100.0)
