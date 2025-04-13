import pandas as pd
import struct
from collections import Counter
import os
# Bản đồ chỉ số feature → tên feature
feature_index_to_name = {
    0: 'arbitration_id',
    1: 'inter_arrival_time',
    10: 'data_entropy',
    11: 'dls',
    -1: 'none'
}

# 📦 B1: Chuyển file CSV cây sang file nhị phân (9 byte/node)
def convert_csv_to_bin(csv_path, bin_path):
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()  # Xóa khoảng trắng

    with open(bin_path, 'wb') as f:
        for _, row in df.iterrows():
            node = int(row['Node']) & 0xFF
            feature = int(row['Feature']) if not pd.isna(row['Feature']) else -1
            threshold = float(row['Threshold']) if not pd.isna(row['Threshold']) else 0.0
            left = int(row['Left_Child']) if not pd.isna(row['Left_Child']) else 0
            right = int(row['Right_Child']) if not pd.isna(row['Right_Child']) else 0

            pred_raw = row['Prediction']
            if pd.isna(pred_raw) or str(pred_raw).upper() == 'FF':
                prediction = 0xFF
            else:
                prediction = int(pred_raw) & 0xFF

            packed = struct.pack('<HffHHB', node, feature, threshold, left, right, prediction)
            f.write(packed)

    print(f"✅ File nhị phân đã được ghi vào: {bin_path}")

# 📥 B2: Đọc cây từ file .bin (dạng dict)
def load_tree_from_bin_small(bin_path):
    tree = {}
    with open(bin_path, 'rb') as f:
        while True:
            bytes_data = f.read(15)
            if not bytes_data:
                break
            node, feature, threshold, left, right, prediction = struct.unpack('<HffHHB', bytes_data)
            tree[node] = {
                'Feature': feature,
                'Threshold': threshold,
                'Left_Child': left,
                'Right_Child': right,
                'Prediction': prediction
            }
    return tree

# 🧠 B3: Dự đoán 1 cây
def predict_from_bin_tree(tree_dict, input_data, verbose=False):
    node = 0
    while True:
        if node not in tree_dict:
            if verbose:
                print(f"❌ Node {node} không tồn tại.")
            return None

        row = tree_dict[node]
        is_leaf = row['Feature'] == -1
        feature_name = None if is_leaf else feature_index_to_name.get(row['Feature'], "-1")

        if is_leaf:
            if verbose:
                print(f"✅ Node {node} là node lá. Prediction = {row['Prediction']}")
            return row['Prediction']

        threshold = row['Threshold']
        feature_value = input_data[feature_name]

        if verbose:
            cmp_str = "<=" if feature_value <= threshold else ">"
            print(f"🧠 Node {node}: {feature_name} ({feature_value:.4f}) {cmp_str} {threshold:.4f}")


        if feature_value <= threshold:
            node = row['Left_Child']
        else:
            node = row['Right_Child']

# 🗳️ B4: Voting từ nhiều cây nhị phân
def vote_predictions_bin(tree_bin_paths, input_data, verbose=False):
    predictions = []
    for bin_path in tree_bin_paths:
        if verbose:
            print(f"\n=> Đang chạy {bin_path}")
        tree = load_tree_from_bin_small(bin_path)
        pred = predict_from_bin_tree(tree, input_data, verbose=verbose)
        predictions.append(pred)

    prediction_counts = Counter(predictions)
    voted_prediction = prediction_counts.most_common(1)[0][0]
    return voted_prediction, prediction_counts

# 🧪 B5: Chạy thử
if __name__ == "__main__":
    # Bước 1: Convert tất cả cây CSV → BIN
    folder_path = "src/LUT"
    tree_count = len([f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))])
    # for i in range(tree_count-1):
    #     csv_path = f"src/LUT/tree_{i}.csv"
    #     bin_path = f"src/BIN/tree_{i}.bin"
    #     convert_csv_to_bin(csv_path, bin_path)

    # Bước 2: Dự đoán với mẫu
    sample_input = {
        'arbitration_id': 342,
        'inter_arrival_time': 0.0,
        'data_entropy': 1.061,
        'dls': 8,
    } #1
    sample_input_2 = {
        'arbitration_id': 977,
        'inter_arrival_time': 0.02,
        'data_entropy': 1.549,
        'dls': 8,
    } #0

    # Bước 3: Voting
    tree_bin_paths = [f"src/BIN/tree_{i}.bin" for i in range(tree_count-1)]
    voted_prediction, prediction_counts = vote_predictions_bin(tree_bin_paths, sample_input, verbose=True)

    print(f"\n🧾 Final Voted Prediction: {voted_prediction} (0: Normal, 1: Attack)")
    print(f"Votes: {prediction_counts}")
