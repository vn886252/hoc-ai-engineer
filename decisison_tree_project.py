from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, classification_report
import numpy as np

# Dữ liệu: [độ tuổi] → mua (1) / không mua (0)
X = np.array([
    [18, 1500], [21, 1700], [24, 2000], [27, 2500], [30, 3500], [33, 4000],[36, 4500],[40, 4600], [43, 4700], [46, 4700], [50, 4800], [54, 5000], [57, 4500], [60, 4400],[64, 4300]
    ])
y = np.array([0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0])

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)

model = DecisionTreeClassifier(random_state=42)
model.fit(X_train, y_train)

du_doan = model.predict(X_test)
print("Dự đoán:", du_doan)
print("Thực tế:", y_test)
print("Độ chính xác:", accuracy_score(y_test, du_doan))

# Dự đoán độ tuổi khách hàng này có mua không?
kh_moi = np.array([[25, 4000]])
print("Dự đoán mua/ko:", model.predict(kh_moi))

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

du_doan = model.predict(X_test)
print("độ chính xác random Forest:", accuracy_score(y_test, du_doan))
print(confusion_matrix(y_test, du_doan))
print(classification_report(y_test, du_doan))