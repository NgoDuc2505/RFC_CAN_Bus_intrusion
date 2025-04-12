import pandas as pd

# Ánh xạ chỉ số feature sang tên cột
feature_index_to_name = {
    0: 'arbitration_id',
    1: 'inter_arrival_time',
    2: 'data_entropy',
    3: 'dls'
}

# Hàm đọc LUT từ file CSV
def load_tree_from_csv(csv_path):
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()  # Xóa khoảng trắng

    # Chuyển đổi giá trị hex sang số nguyên
    for col in ['Node', 'Feature', 'Threshold', 'Left_Child', 'Right_Child', 'Prediction']:
        df[col] = df[col].apply(lambda x: int(str(x), 16) if str(x) != 'FF' else -1)
    
    return df

# Hàm dự đoán giống random forest dựa trên cây
def predict_from_tree(tree_df, input_data, verbose=False):
    node = 0
    while True:
        matches = tree_df[tree_df['Node'] == node]
        if matches.empty:
            if verbose:
                print(f"❌ Node {node} không tồn tại.")
            return None
        row = matches.iloc[0]
        
        if row['Prediction'] != -1:
            if verbose:
                print(f"✅ Node {node} là node lá. Prediction = {row['Prediction']}")
            return row['Prediction']

        feature_idx = row['Feature']
        feature_name = feature_index_to_name.get(feature_idx, None)
        threshold = row['Threshold'] / (1 << 20)  # Fixed-point Q12.20
        feature_value = input_data[feature_name]

        if verbose:
            print(f"🧠 Node {node}: {feature_name} ({feature_value:.6f}) "
                  f"{'<= ' if feature_value <= threshold else '>  '} {threshold:.6f}")

        if feature_value <= threshold:
            node = row['Left_Child']
        else:
            node = row['Right_Child']

# Main chạy như bạn yêu cầu
if __name__ == "__main__":
    csv_path = "src/LUT/split_model_v4_00.csv"  # Đường dẫn tới file LUT CSV
    tree_df = load_tree_from_csv(csv_path)

    # Dữ liệu đầu vào
    sample_input = {
        'arbitration_id': 342,
        'inter_arrival_time': 0.0,
        'data_entropy': 1.061,
        'dls': 8,
    }
    sample_input_2 = {
        'arbitration_id': 977,
        'inter_arrival_time': 0.02,
        'data_entropy': 1.549,
        'dls': 8,
    }

    # Dự đoán
    pred = predict_from_tree(tree_df, sample_input_2, verbose=True)
    print(f"\n🧾 Prediction: {pred} (0: Normal, 1: Attack)")
