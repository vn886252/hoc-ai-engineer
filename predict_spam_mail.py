from sklearn.metrics import confusion_matrix, classification_report, accuracy_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
import numpy as np

#[so_tu_khoa_quang_cao, link_la, nguoi_quen] 1 spam 0 ko spam
X = np.array([[6,2,1],[2,1,1],[0,1,4],[3,2,5],[1,0,0],[5,1,0],[6,1,2],[3,0,0],[0,3,0],[10,1,6],
             [2,0,4],[3,1,6],[0,0,6],[6,1,2],[2,1,1],[4,1,3],[4,4,0],[1,2,0],[2,2,0],[6,0,0],
             [2,1,8],[4,0,7],[2,0,3],[4,1,2],[9,1,9],[4,1,9],[6,2,12],[0,1,0],[7,0,9],[1,0,7]   

])
Y = np.array ([1,0,0,0,0,1,1,1,1,0,
               0,0,0,1,1,0,1,1,1,1,
               0,0,0,1,0,0,0,1,1,0])

X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.3,random_state=42, stratify=Y)

model = DecisionTreeClassifier(random_state=42)
model.fit(X_train,Y_train)

du_doan = model.predict(X_test)
print("dự đoán:",du_doan)
print("thực tế:", Y_test)
print("độ chính xác decision tree:", accuracy_score(Y_test,du_doan))

mail_moi = np.array([[1,0,2]])
print("dự đoán mail rác:", model.predict(mail_moi))

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train,Y_train)

du_doan = model.predict(X_test)
print("độ chính xác random forest:", accuracy_score(Y_test, du_doan))
print(confusion_matrix(Y_test,du_doan))
print(classification_report(Y_test,du_doan))

#mô hình random forest tốt hơn nhiều cho tỉ lệ chính xác cao hơn, điều này giúp hạn chế mail spam vượt qua rất nhiều 