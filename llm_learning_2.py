from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

mae = mean_absolute_error(y_test, du_doan)
mse = mean_squared_error(y_test, du_doan)
r2 = r2_score(y_test, du_doan)

print("MAE (sai số trung bình tuyệt đối):", mae)
print("MSE (sai số bình phương trung bình):", mse)
print("R² (độ phù hợp, 0-1, càng gần 1 càng tốt):", r2)