import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

# ===============================
# 1. VERİYİ OKU
# ===============================
df = pd.read_excel("final.xlsx")

# başlıkları temizle
df.columns = df.columns.str.strip()

# ===============================
# 2. HEDEF
# ===============================
target = "ET"

# ===============================
# 3. DOY -> MEVSİMSEL DÖNÜŞÜM
# ===============================
df["DOY_sin"] = np.sin(2 * np.pi * df["DOY"] / 365)
df["DOY_cos"] = np.cos(2 * np.pi * df["DOY"] / 365)

# ===============================
# 4. FEATURE SETİ (YEAR HAM HALİYLE!)
# ===============================
features = [
    "Year",
    "NW Air Temp in degrees C",
    "NW RH in %",
    "NW Rs in MJ/m^2",
    "NW Rn in MJ/m^2",
    "NW 2-m Wind Speed in m/s",
    "DOY_sin",
    "DOY_cos"
]

# ===============================
# 5. SADECE GEREKLİ SATIRLAR
# ===============================
df = df[[target] + features].dropna()

X = df[features]
y = df[target]

print("Toplam kullanılabilir satır:", len(df))

# ===============================
# 6. TRAIN / TEST
# ===============================
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42
)

# ===============================
# 7. MODEL (SCALER + RIDGE)
# ===============================
model = Pipeline([
    ("scaler", StandardScaler()),
    ("ridge", Ridge(alpha=1.0))
])

# ===============================
# 8. EĞİTİM
# ===============================
model.fit(X_train, y_train)

# ===============================
# 9. DEĞERLENDİRME
# ===============================
pred = model.predict(X_test)

print("MAE :", mean_absolute_error(y_test, pred))
print("R2  :", r2_score(y_test, pred))

# ===============================
# 10. MODELİ KAYDET
# ===============================
joblib.dump(model, "../cotton_et_model2.pkl")
print("Model kaydedildi: model2.pkl")
