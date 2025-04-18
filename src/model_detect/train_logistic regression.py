# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# import seaborn as sns
# from sklearn.model_selection import train_test_split
# from sklearn.linear_model import LogisticRegression
# from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
# from sklearn.preprocessing import LabelEncoder, StandardScaler
# import joblib

# def preprocess_data(df):
#     df = df.copy()

#     for col in ['arbitration_id', 'data_field']:
#         if df[col].dtype == object:
#             df[col] = df[col].apply(lambda x: int(x, 16) if isinstance(x, str) else x)

#     return df

# def train_logistic_regression():
#     # Đọc dữ liệu
#     df = pd.read_csv("src/datasets_release/candata_train_demo_new.csv")
    
#     # Tiền xử lý
#     df = preprocess_data(df)

#     # Hiển thị thông tin cơ bản
#     print("Data Overview:")
#     print(df.head())
#     print("\nData Info:")
#     print(df.info())

#     # Tách đặc trưng và nhãn
#     X = df.drop(columns=['attack', 'timestamp'])
#     y = df['attack']

#     # Chuẩn hóa đặc trưng để logistic hoạt động tốt hơn
#     scaler = StandardScaler()
#     X_scaled = scaler.fit_transform(X)

#     # Chia dữ liệu
#     X_train, X_test, y_train, y_test = train_test_split(
#         X_scaled, y, test_size=0.2, random_state=42, stratify=y
#     )

#     # Huấn luyện Logistic Regression
#     model = LogisticRegression(
#         solver='lbfgs', max_iter=1000, random_state=42
#     )
#     model.fit(X_train, y_train)

#     # Lưu mô hình và scaler
#     joblib.dump(model, "candata_train_demo_new.pkl")
#     joblib.dump(scaler, "scaler_candata.pkl")
#     print("\nModel trained and saved as candata_train_demo_new.pkl")

#     # Dự đoán
#     predictions = model.predict(X_test)

#     # Đánh giá
#     accuracy = accuracy_score(y_test, predictions)
#     print(f"\nModel Accuracy: {accuracy:.4f}")
#     print("\nClassification Report:")
#     print(classification_report(y_test, predictions))

#     # Ma trận nhầm lẫn
#     cm = confusion_matrix(y_test, predictions)
#     plt.figure(figsize=(8,6))
#     sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
#     plt.title('Confusion Matrix')
#     plt.xlabel('Predicted')
#     plt.ylabel('Actual')
#     plt.show()

# if __name__ == "__main__":
#     train_logistic_regression()


import joblib
import numpy as np

# Tải mô hình và bộ chuẩn hóa từ các tệp .pkl
model = joblib.load("src/datasets_release/candata_train_demo_new.pkl")
scaler = joblib.load("src/datasets_release/scaler_candata.pkl")

# In thông tin chi tiết của mô hình Logistic Regression
print("Logistic Regression Model Details:")
print(f"Intercept: {model.intercept_}")
print(f"Coefficients: \n{model.coef_}")

# In thông tin chi tiết của bộ chuẩn hóa StandardScaler
print("\nStandardScaler Details:")
print(f"Mean: \n{scaler.mean_}")
print(f"Scale: \n{scaler.scale_}")
