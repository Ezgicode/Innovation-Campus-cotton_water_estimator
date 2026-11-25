import pandas as pd

df = pd.read_excel("noktalı1.xlsx")

# 1. Sütun adlarını temizle (boşluk vs.)
df.columns = df.columns.str.strip()

# 2. Sadece kullanacağımız kolonlar
cols = [
    "ET",
    "Year",
    "DOY",
    "NW Air Temp in degrees C",
    "NW RH in %",
    "NW Rs in MJ/m^2",
    "NW Rn in MJ/m^2",
    "NW 2-m Wind Speed in m/s"
]

df = df[cols]

# 3. NULL olan satırları sil
df = df.dropna()

print("Kalan satır sayısı:", len(df))
