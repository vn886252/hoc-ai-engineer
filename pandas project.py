import pandas as pd
data = {
    "ten": ["Khoa", "Hồ", "Sang"],
    "diem_toan": [10, 8, 5],
    "diem_van": [7, 6, 4],
    "diem_anh": [6 ,10, 4]
    }
df = pd.DataFrame(data)

df["diem_trung_binh"] = df[["diem_toan","diem_van","diem_anh"]].mean(axis=1)
print(df.loc[df["diem_trung_binh"].idxmax()])
print(df.sort_values("diem_trung_binh", ascending=False).head(1))

print(df[df["diem_trung_binh"]>=7])



