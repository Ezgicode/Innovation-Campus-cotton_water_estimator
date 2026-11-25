import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score

df = pd.read_excel("final.xlsx")

# başlık boşluklarını temizle
df.columns = df.columns.str.strip()

target = "ET"

# gerekli kolonları seç (Year'ı kesin çıkar, DOY'yi dönüştüreceğiz)
base_features = [
    "DOY",
    "NW Air Temp in degrees C",
    "NW RH in %",
    "NW Rs in MJ/m^2",
    "NW Rn in MJ/m^2",
    "NW 2-m Wind Speed in m/s"
]

# sadece ihtiyacımız olan kolonları al
df = df[[target] + base_features].copy()

# boşları at
df = df.dropna(subset=[target] + base_features)

# --- DOY -> mevsimsel dönüşüm (sin/cos) ---
doy = df["DOY"].astype(float)

# 365.25 da kullanılabilir, 365 yeterli
df["sin_doy"] = np.sin(2 * np.pi * doy / 365.0)
df["cos_doy"] = np.cos(2 * np.pi * doy / 365.0)

# ham DOY'yi kaldır (istersen bırakabilirsin ama genelde kaldırmak daha temiz)
df = df.drop(columns=["DOY"])

# X / y
X = df.drop(columns=[target])
y = df[target]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = Pipeline([
    ("scaler", StandardScaler()),
    ("ridge", Ridge(alpha=1.0))
])

model.fit(X_train, y_train)
pred = model.predict(X_test)

print("MAE:", mean_absolute_error(y_test, pred))
print("R2 :", r2_score(y_test, pred))

print("\nKullanılan feature'lar:", list(X.columns))
