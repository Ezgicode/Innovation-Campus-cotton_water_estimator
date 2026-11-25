import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score

# ===============================
# 1. VERİYİ OKU
# ===============================
df = pd.read_excel("final.xlsx")

# Başlık temizliği (ET , gibi saçmalıklar için)
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
# 4. YEAR NORMALIZATION (BAĞLAM)
# ===============================
df["Year_norm"] = (df["Year"] - df["Year"].mean()) / df["Year"].std()

# ===============================
# 5. FEATURE SETİ (NET VE TEMİZ)
# ===============================
features = [
    "NW Air Temp in degrees C",
    "NW RH in %",
    "NW Rs in MJ/m^2",
    "NW Rn in MJ/m^2",
    "NW 2-m Wind Speed in m/s",
    "DOY_sin",
    "DOY_cos",
    "Year_norm"
]

# ===============================
# 6. SADECE GEREKLİ SATIRLARI AL
# ===============================
df = df.dropna(subset=[target] + features)

X = df[features]
y = df[target]

print("Toplam kullanılabilir satır:", len(df))

# ===============================
# 7. TRAIN / TEST
# ===============================
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42
)

# ===============================
# 8. MODEL
# ===============================
model = Pipeline([
    ("scaler", StandardScaler()),
    ("ridge", Ridge(alpha=1.0))
])

# ===============================
# 9. EĞİTİM
# ===============================
model.fit(X_train, y_train)

# ===============================
# 10. DEĞERLENDİRME
# ===============================
pred = model.predict(X_test)

print("MAE :", mean_absolute_error(y_test, pred))
print("R2  :", r2_score(y_test, pred))


import joblib

joblib.dump(model, "cotton_et_model.pkl")
print("Model kaydedildi")
