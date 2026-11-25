# Dataset card: Bushland, Texas cotton lysimeter data (cleaned subset)

## Summary
Daily crop evapotranspiration (ET) of upland cotton (*Gossypium hirsutum* L.) measured with large precision weighing lysimeters at the USDA-ARS Conservation and Production Research Laboratory, Bushland, Texas (35.19° N, 102.09° W, 1,170 m), together with on-site weather measurements from the northwest (NW) lysimeter field.

## Source
USDA-ARS Bushland, Texas Cotton Datasets, published on the USDA Ag Data Commons under **Creative Commons CC0 1.0** (public domain). Contact: Steven R. Evett, USDA-ARS.

- **Weighing Lysimeter Data for The Bushland, Texas, Cotton Datasets**: weather variables and ET used by the model. https://doi.org/10.15482/USDA.ADC/25114670.v1
- **Growth and Yield Data for the Bushland, Texas, Cotton Datasets**: companion dataset used during data exploration.

## Files in this repository
| File | Rows | Description |
|---|---|---|
| `script/Data_Nan.xlsx` | 1,463 | Daily records extracted from the source files, including missing values |
| `script/noktalı1.xlsx` | 1,463 | Same data after converting decimal commas to dots (`script1.py`) |
| `model_xgboost/final.xlsx` | 570 | Complete rows only (`lastdb.py`); used for all training and evaluation |

## Columns
| Column | Unit | Description |
|---|---|---|
| `ET` | mm/day | Measured cotton evapotranspiration (target) |
| `Year`, `DOY` | – | Season and day of year (DOY 115–365) |
| `NW Air Temp in degrees C` | °C | Mean air temperature |
| `NW RH in %` | % | Relative humidity |
| `NW Rs in MJ/m^2` | MJ/m²/day | Incoming solar radiation |
| `NW Rn in MJ/m^2` | MJ/m²/day | Net radiation |
| `NW 2-m Wind Speed in m/s` | m/s | Wind speed at 2 m |

Seasons: 2000 (134 days), 2001 (131), 2008 (83), 2012 (222).

## Known characteristics and limitations
- Single semi-arid site; four seasons.
- Seasons were managed with different irrigation regimes (full, deficit or dryland). Seasonal ET/ET₀ is 0.82 in 2012 and 0.34–0.46 in 2000, 2001 and 2008, which is consistent with 2012 being well-watered; this label is inferred and not taken from the field logs.
- The source ET values are lysimeter measurements that the publisher describes as raw data after quality control.
- Rows with any missing value were removed, so some periods of each season are not covered.

## Citation
Evett, S. R., et al. Weighing Lysimeter Data for The Bushland, Texas, Cotton Datasets. USDA-ARS Ag Data Commons. https://doi.org/10.15482/USDA.ADC/25114670.v1

Evett, S. R., et al. Growth and Yield Data for the Bushland, Texas, Cotton Datasets. USDA-ARS Ag Data Commons.
