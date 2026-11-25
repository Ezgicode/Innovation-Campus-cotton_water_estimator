import pandas as pd

# Temizlenmiş dataframe'in olduğu dosya
df = pd.read_excel("noktalı1.xlsx")

# Kullanılan kolonlar
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

# Null satırları sil
df_clean = df.dropna().reset_index(drop=True)

print("Kalan satır sayısı:", len(df_clean))  # 570 görmelisin

# Yeni Excel olarak kaydet
df_clean.to_excel("final.xlsx", index=False)

print("✅final.xlsx oluşturuldu")
