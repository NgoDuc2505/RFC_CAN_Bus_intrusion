import pandas as pd
import joblib


def load_model(model_path):
    return joblib.load(model_path)

def predict(model, input_data):
    df = pd.DataFrame([input_data])
    prediction = model.predict(df)
    probability = model.predict_proba(df)
    return prediction[0], probability[0]

if __name__ == "__main__":
    model_path = "random_forest_model_v2.pkl"
    model = load_model(model_path)
    
    sample_input = {
        'timestamp': 0.050,
        'id': 300,
        'dlc': 4,
        'data_entropy': 2.10,
    }
    
    sample_input_2 = {
        'timestamp': 1.250,
        'arbitration_id': 999,
        'dlc': 8,
        'data_entropy': 0.5,
        'packet_rate': 25,
        'inter_arrival_time': 0.010
    }
    
    pred, prob = predict(model, sample_input)
    print(f"Prediction: {pred} (0: Normal, 1: Attack)")
    print(f"Probability: {prob}")

#Prediction: 0 (0: Normal, 1: Attack)
#Probability: [0.52 0.48]