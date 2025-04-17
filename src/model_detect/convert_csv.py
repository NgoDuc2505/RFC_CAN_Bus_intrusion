import pandas as pd
import numpy as np
from collections import Counter

def calculate_entropy(hex_data):
    if isinstance(hex_data, float) or not hex_data or len(hex_data) % 2 != 0:
        return 0

    byte_values = [hex_data[i:i+2] for i in range(0, len(hex_data), 2)]
    byte_counts = Counter(byte_values)
    total_bytes = len(byte_values)
    probabilities = [count / total_bytes for count in byte_counts.values()]
    entropy = -sum(p * np.log2(p) for p in probabilities if p > 0)
    return round(entropy, 3)

def preprocess_dataframe(df):
    df["arbitration_id"] = df["arbitration_id"].apply(lambda x: int(x, 16))
    df["timestamp"] = df["timestamp"].astype(float)
    df["inter_arrival_time"] = df.groupby("arbitration_id")["timestamp"].diff().fillna(0).round(4)
    return df

def process_single_csv(input_file, output_file, label=1):
    df = pd.read_csv(input_file)
    print(f"File {input_file} có {len(df)} mẫu")

    df = preprocess_dataframe(df)
    df["data_entropy"] = df["data_field"].apply(calculate_entropy)
    df["dls"] = df["data_field"].apply(lambda x: len(str(x).replace(" ", "")) // 2)

    df.drop(columns=["timestamp", "data_field"], inplace=True)
    df["label"] = label

    df.to_csv(output_file, index=False)
    print(f"Xuất kết quả ra: {output_file} ({len(df)} mẫu)")

# ⚙️ Chạy xử lý
input_file = "src/datasets_release/test_01_known_vehicle_known_attack/DoS-3.csv"
output_file = "src/datasets_release/test_01_known_vehicle_known_attack/DoS-3-attack.csv"
process_single_csv(input_file, output_file, label=1)
