"""Model v2 for daily cotton ET (Bushland, Texas lysimeter data).

What changed compared with v1 (model_xgboost/train4.py, left untouched):
  * The raw "Year" feature is removed. In v1 it acted as a shortcut for
    differences between seasons, so predictions for years after 2012 were
    extrapolated upwards (same weather: 3.5 mm/day in 2000, 11.2 in 2025).
  * Physics-based features: FAO-56 Penman-Monteith reference ET (ET0) and
    vapour pressure deficit.
  * Water regime feature: 2012 behaves like a well-watered season
    (seasonal ET/ET0 = 0.82) while 2000, 2001 and 2008 behave like
    water-limited seasons (0.34-0.46). This is inferred from the data.
  * Random Forest instead of Ridge, to capture non-linear effects.
  * Evaluation on the same 80/20 split as v1 (random_state=42), 5-fold CV,
    and a stricter leave-one-season-out test.

Run:  python train_v2.py
"""
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupKFold, KFold, cross_val_predict, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from features import FEATURES, RAW_COLUMNS, build_features

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "model_xgboost" / "final.xlsx"
OUT = HERE / "results"
OUT.mkdir(exist_ok=True)
FULL_IRRIGATION_SEASONS = {2012}


def load_data():
    df = pd.read_excel(DATA)
    df.columns = df.columns.str.strip()
    df = df.dropna(subset=["ET", "Year", "DOY", *RAW_COLUMNS]).reset_index(drop=True)
    return df


def v1_features(df):
    x = df[["Year", *RAW_COLUMNS]].copy()
    x["DOY_sin"] = np.sin(2 * np.pi * df["DOY"] / 365)
    x["DOY_cos"] = np.cos(2 * np.pi * df["DOY"] / 365)
    return x


def v2_features(df):
    r = df.rename(columns=RAW_COLUMNS)
    return build_features(r.temp, r.rh, r.rs, r.rn, r.wind, r.DOY,
                          r.Year.isin(FULL_IRRIGATION_SEASONS))


def make_v1():
    return Pipeline([("scaler", StandardScaler()), ("ridge", Ridge(alpha=1.0))])


def make_v2():
    return RandomForestRegressor(n_estimators=400, min_samples_leaf=3, random_state=0, n_jobs=-1)


def scores(y, p):
    return {"MAE": round(float(mean_absolute_error(y, p)), 3),
            "RMSE": round(float(mean_squared_error(y, p) ** 0.5), 3),
            "R2": round(float(r2_score(y, p)), 3)}


def evaluate(name, x, y, years, make):
    xtr, xte, ytr, yte = train_test_split(x, y, test_size=0.2, random_state=42)
    pred = make().fit(xtr, ytr).predict(xte)
    kfold = cross_val_predict(make(), x, y, cv=KFold(5, shuffle=True, random_state=0))
    loso = cross_val_predict(make(), x, y, groups=years, cv=GroupKFold(4))
    limited = ~years.isin(FULL_IRRIGATION_SEASONS)
    res = {"test_split_80_20": scores(yte, pred),
           "cv_5fold": scores(y, kfold),
           "leave_one_season_out_water_limited": scores(y[limited], loso[limited])}
    print(name, json.dumps(res, indent=2))
    return res, yte, pred


def main():
    df = load_data()
    y, years = df["ET"], df["Year"]
    print(f"Rows: {len(df)}  Seasons: {sorted(years.unique())}")
    print("Seasonal ET/ET0 ratio:")
    et0 = v2_features(df)["et0"]
    print((df.groupby("Year")["ET"].sum() / et0.groupby(df["Year"]).sum()).round(2))

    v1, _, _ = evaluate("v1 (Ridge + Year)", v1_features(df), y, years, make_v1)
    x2 = v2_features(df)
    v2, yte, pred = evaluate("v2 (Random Forest + FAO-56)", x2, y, years, make_v2)

    model = make_v2().fit(x2, y)
    joblib.dump(model, HERE / "cotton_et_model_v2.pkl")
    importances = dict(sorted(zip(FEATURES, model.feature_importances_.round(3).tolist()),
                              key=lambda kv: -kv[1]))
    json.dump({"rows": len(df), "v1": v1, "v2": v2, "v2_feature_importance": importances},
              open(OUT / "metrics_v1_vs_v2.json", "w"), indent=2)
    pd.DataFrame({"measured_et": yte.values, "predicted_et_v2": pred}).to_csv(
        OUT / "test_predictions_v2.csv", index=False)
    print("Saved cotton_et_model_v2.pkl and results/")


if __name__ == "__main__":
    main()
