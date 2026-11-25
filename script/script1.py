import pandas as pd

input_file = "virgüllü.xlsx"
output_file = "noktalı1.xlsx"

# 1️⃣ HER ŞEYİ STRING OKU
df = pd.read_excel(input_file, dtype=str)
df.columns = df.columns.str.strip()


# 2️⃣ VİRGÜL → NOKTA
df = df.map(lambda x: x.replace(",", ".") if isinstance(x, str) else x)

# 3️⃣ BOŞLARI NaN YAP
df = df.replace("", pd.NA)

# 4️⃣ KAYDET
df.to_excel(output_file, index=False)

print(" noktalı dosyamız umarım oluşturulmuştur.")






