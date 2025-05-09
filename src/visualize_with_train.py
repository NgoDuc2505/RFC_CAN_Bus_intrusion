import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from sklearn.model_selection import train_test_split

# Đọc dữ liệu từ file CSV
def load_data(file_path):
    df = pd.read_csv(file_path)
    return df

# Vẽ biểu đồ Accuracy theo số lượng cây trong Random Forest
def plot_accuracy_vs_estimators(estimators, accuracies):
    plt.figure(figsize=(8, 5))
    plt.plot(estimators, accuracies, marker='o', linestyle='-', color='b', label="Accuracy")
    plt.xlabel("Số lượng cây trong Random Forest")
    plt.ylabel("Accuracy")
    plt.title("Accuracy theo số lượng cây trong Random Forest")
    plt.legend()
    plt.grid()
    plt.savefig("accuracy_vs_estimators.png")
    plt.show()

# Vẽ Confusion Matrix
def plot_confusion_matrix(y_true, y_pred):
    cm = confusion_matrix(y_true, y_pred)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm)
    disp.plot(cmap=plt.cm.Blues)
    plt.title("Confusion Matrix")
    plt.savefig("confusion_matrix.png")
    plt.show()

# Vẽ Feature Importance
def plot_feature_importance(model, feature_names):
    feature_importances = model.feature_importances_
    plt.figure(figsize=(10, 5))
    sns.barplot(x=feature_importances, y=feature_names, palette="viridis")
    plt.xlabel("Mức độ quan trọng")
    plt.ylabel("Feature")
    plt.title("Feature Importance trong Random Forest")
    plt.savefig("feature_importance.png")
    plt.show()

# Hàm chính để huấn luyện và vẽ biểu đồ
def main(csv_file):
    df = load_data(csv_file)
    
    # Xác định cột nhãn (label)
    X = df.drop(columns=["attack"], errors='ignore')
    y = df["attack"] if "attack" in df.columns else None
    
    if y is None:
        raise ValueError("Dataset không chứa cột 'attack'. Kiểm tra lại file CSV.")
    
    # Chia tập train/test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Huấn luyện với số lượng cây khác nhau
    estimators = [1, 5, 10, 50, 100]
    accuracies = []
    for n in estimators:
        model = RandomForestClassifier(n_estimators=n, random_state=42, min_samples_split=2, criterion='gini')
        model.fit(X_train, y_train)
        accuracies.append(model.score(X_test, y_test))
    
    # Huấn luyện mô hình cuối cùng
    final_model = RandomForestClassifier(n_estimators=100, random_state=42, min_samples_split=2, criterion='gini')
    final_model.fit(X_train, y_train)
    y_pred = final_model.predict(X_test)
    
    # Vẽ các biểu đồ
    plot_accuracy_vs_estimators(estimators, accuracies)
    plot_confusion_matrix(y_test, y_pred)
    plot_feature_importance(final_model, X.columns)
    
    print("Biểu đồ đã được lưu!")

# Chạy script
if __name__ == "__main__":
    main("merged_can_data.csv")
