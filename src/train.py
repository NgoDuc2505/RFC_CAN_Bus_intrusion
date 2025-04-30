import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder
import joblib

def preprocess_data(df):
    # Tiền xử lý dữ liệu
    df = df.copy()
    
    # Xử lý các cột hex nếu cần
    for col in ['arbitration_id', 'data_field']:
        if df[col].dtype == object:
            # Chuyển hex sang số nguyên
            df[col] = df[col].apply(lambda x: int(x, 16) if isinstance(x, str) else x)
    
    return df

def train_and_visualize():
    # Đọc dữ liệu
    df = pd.read_csv("datasets_release/balanced_dataset.csv")
    
    # Tiền xử lý
    df = preprocess_data(df)
    
    # Kiểm tra dữ liệu
    print("Data Overview:")
    print(df.head())
    print("\nData Info:")
    print(df.info())
    
    # Chuẩn bị features và target
    X = df.drop(columns=['attack', 'timestamp'])  # Bỏ timestamp nếu không cần
    y = df['attack']
    
    # Chia tập dữ liệu
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Huấn luyện mô hình
    model = RandomForestClassifier(
        n_estimators=21,  # Tăng số cây để cải thiện hiệu suất
        min_samples_split=2,
        criterion='gini',
        random_state=42,
        max_depth=9,  # Để cây phát triển tự nhiên
        max_features='sqrt',  # Tốt cho dữ liệu phân loại
        n_jobs=-1  # Sử dụng tất cả CPU
    )
    
    model.fit(X_train, y_train)
    
    # Lưu mô hình
    joblib.dump(model, "datasets_release/can-data-w.pkl")
    print("\nModel trained and saved as model can-data.pkl")
    
    # Đánh giá
    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    print(f"\nModel Accuracy: {accuracy:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, predictions))
    
    # Ma trận nhầm lẫn
    cm = confusion_matrix(y_test, predictions)
    plt.figure(figsize=(8,6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.title('Confusion Matrix')
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.show()
    
    # Feature importance
    feature_imp = pd.Series(model.feature_importances_, index=X.columns)
    feature_imp.nlargest(10).plot(kind='barh')
    plt.title('Top 10 Important Features')
    plt.show()

if __name__ == "__main__":
    train_and_visualize()