import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score

df = pd.read_excel("final.xlsx")

# başlık boşluklarını temizle (ET , gibi)
df.columns = df.columns.str.strip()

# hedef + feature seç
target = "ET"
features = [c for c in df.columns if c != target]

# boşları at
df = df.dropna(subset=[target] + features)

X = df[features]
y = df[target]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = Pipeline([
    ("scaler", StandardScaler()),
    ("ridge", Ridge(alpha=1.0))
])

X_new = pd.DataFrame([{
    "Year": 2024,                 # ister koy, ister çıkar
    "DOY": 190,
    "NW Air Temp in degrees C": 32.5,
    "NW RH in %": 45.0,
    "NW Rs in MJ/m^2": 22.1,
    "NW Rn in MJ/m^2": 14.8,
    "NW 2-m Wind Speed in m/s": 3.2
}])


model.fit(X_train, y_train)
pred = model.predict(X_new)

print(pred)
#print("MAE:", mean_absolute_error(y_test, pred))
#print("R2 :", r2_score(y_test, pred))
print(df.head())
print(df["ET"].describe())