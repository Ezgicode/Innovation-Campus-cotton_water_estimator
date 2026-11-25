# Model card: Cotton daily evapotranspiration (ET) model

## Purpose
Estimate daily cotton water use (ET, mm/day) from weather data, as the basis for an irrigation recommendation. Intended for education, research and decision support with expert oversight; not for autonomous irrigation control.

## Versions
| | v1 | v2 (current) |
|---|---|---|
| Code | `model_xgboost/train4.py` | `model_v2/train_v2.py` |
| Algorithm | StandardScaler + Ridge (α = 1.0) | Random Forest (400 trees, min_samples_leaf = 3) |
| Features | year, air temperature, RH, Rs, Rn, wind, sin/cos(DOY) | FAO-56 ET₀, VPD, air temperature, RH, Rs, Rn, wind, sin/cos(DOY), water regime |
| Saved model | `cotton_et_model2.pkl` | `model_v2/cotton_et_model_v2.pkl` (created by `train_v2.py`) |

## Training data
570 complete days from the Bushland, Texas lysimeter dataset (2000, 2001, 2008, 2012). See `datasetcard.md`.

## Evaluation
| Evaluation | v1 MAE / RMSE / R² | v2 MAE / RMSE / R² |
|---|---|---|
| 80/20 split, `random_state=42` (114 test days) | 1.13 / 1.48 / 0.60 | 0.54 / 0.83 / 0.87 |
| 5-fold CV (shuffled) | 1.14 / 1.50 / 0.64 | 0.63 / 0.90 / 0.87 |
| Leave-one-season-out, water-limited seasons | 1.05 / 1.31 / 0.13 | 0.98 / 1.19 / 0.29 |

Full numbers: `model_v2/results/metrics_v1_vs_v2.json`.

## Why v1 was replaced
v1 relies heavily on the year, which mostly encodes differences in water availability between the four seasons. With the same weather it predicts 3.5 mm/day for 2000, 7.2 for 2012 and 11.2 for 2025, so predictions for years after 2012 are extrapolated upwards.

## Limitations
- One site and four seasons; generalisation to unseen seasons is modest (leave-one-season-out R² 0.29) and has not been tested in other regions.
- The water-regime feature is inferred from the data.
- Random Forests do not extrapolate beyond the training range.
- At inference time, weather comes from NASA POWER (a gridded product) while training used on-site measurements; net radiation is approximated as 0.75 × Rs.

## Usage
```bash
cd model_v2
python train_v2.py
streamlit run app_v2.py
```
