import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib

def train():
    df = pd.read_csv("src/datasets_release/can_data_v7_2.csv")
    X = df.drop(columns=['label'])
    y = df['label']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier(#n_estimators=20,
                                   n_estimators=17,
                                   min_samples_split=2,
                                  #  max_depth= 10,
                                   max_depth= 8,
                                   max_leaf_nodes=30,
                                   random_state=42,
                                   criterion='gini',
                                    n_jobs=-1)
    model.fit(X_train, y_train)

    joblib.dump(model, "src/datasets_release/random_forest_model_v4_lite.pkl")
    print("Model trained and saved as random_forest_model.pkl")

    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    print(f"Model Accuracy: {accuracy:.4f}")
    print("Classification Report:")
    print(classification_report(y_test, predictions))
    print("Confusion Matrix:")
    print(confusion_matrix(y_test, predictions))
    #print(f"Predictions: {predictions}")

if __name__ == "__main__":
    train()