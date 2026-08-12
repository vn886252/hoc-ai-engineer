import pandas as pd
data = {
        "mon_hoc": ["Văn","Toán","Anh","Văn"],
        "diem": [4,10,5,6]
        }
df = pd.DataFrame(data)

print(df.groupby("mon_hoc")["diem"].mean())


open_file = pd.read_csv(r"E:\lesson\baitap\industry.csv")
print(open_file.head())
print(open_file.info())
print(open_file.describe())