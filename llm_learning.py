from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import numpy as np

so_nam = np.array([1, 3, 4, 5, 9, 10, 12, 15, 17, 20]).reshape(-1, 1)
muc_luong = np.array([3500, 5500, 6000, 7000, 8500, 11500, 12500, 14000, 16000,19000])

X_train, X_test, y_train, y_test = train_test_split(so_nam, muc_luong, test_size=0.5, random_state=42)

model = LinearRegression()
model.fit(X_train,y_train)

du_doan = model.predict(X_test)
print("Dự đoán:", du_doan)
print("Thực tế:", y_test)

print("Độ dốc (a):", model.coef_)
print("Điểm cắt:", model.intercept_)

so_nam_moi = np.array([[7]])
print("lương dự đoán cho 7 năm là:", model.predict((so_nam_moi)))

from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

mae = mean_absolute_error(y_test, du_doan)
mse = mean_squared_error(y_test, du_doan)
r2 = r2_score(y_test, du_doan)

print("MAE (sai số trung bình tuyệt đối):", mae)
print("MSE (sai số bình phương trung bình):", mse)
print("R² (độ phù hợp, 0-1, càng gần 1 càng tốt):", r2)