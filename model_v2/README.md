# Cotton ET model v2

New version of the cotton water requirement model. **Nothing outside this folder was changed**; the original
scripts (`../model_xgboost/train*.py`), models and apps (`../apiconnect`, `../demoweb`) are kept as they were.

## Why v2?
The v1 Ridge model (`train4.py`) uses the raw `Year` as a feature. Because the four seasons in the data differ
mainly in water availability, the year became a shortcut: with identical weather v1 predicts 3.5 mm/day for 2000
and 11.2 mm/day for 2025. Any prediction for a year after 2012 is extrapolated.

## What changed
| | v1 | v2 |
|---|---|---|
| Model | Ridge regression | Random Forest (400 trees) |
| Year feature | yes | **removed** |
| Physics features | – | FAO-56 Penman-Monteith ET₀, vapour pressure deficit |
| Water regime | – | full vs. limited irrigation (2012 ≈ well-watered, ET/ET₀ = 0.82; 2000/2001/2008 water-limited, 0.34–0.46) |
| NASA helper | skips selected date, date not shown | tries selected date first, shows date used, uses site elevation |

## Results (570 days, same 80/20 split as v1, `random_state=42`)
| Evaluation | v1 MAE / R² | v2 MAE / R² |
|---|---|---|
| Test split (114 days) | 1.13 / 0.60 | **0.54 / 0.87** |
| 5-fold cross-validation | 1.14 / 0.64 | **0.63 / 0.87** |
| Leave-one-season-out (water-limited seasons) | 1.05 / 0.13 | **0.98 / 0.29** |

Full numbers: `results/metrics_v1_vs_v2.json`.

## Run
```
pip install streamlit scikit-learn pandas openpyxl joblib requests
python train_v2.py      # retrains and writes cotton_et_model_v2.pkl + results/
streamlit run app_v2.py
```

## Limitations
* Only four seasons from one site; the water-regime label is inferred from the data, not from the field logs.
* Leave-one-season-out performance is still modest: generalising to new seasons and regions needs more data.
* Net radiation from NASA is approximated as 0.75 × Rs; rainfall is entered manually.

Data: USDA-ARS Bushland, Texas cotton weighing lysimeter datasets, https://doi.org/10.15482/USDA.ADC/25114670.v1 (CC0).
