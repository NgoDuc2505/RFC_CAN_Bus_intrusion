import pandas as pd
from collections import Counter
import struct

# Ánh xạ chỉ số feature sang tên cột
feature_index_to_name = {
    0: 'timestamp',
    1: 'arbitration_id',
    10: 'data_field',
    11: 'none'
}

# Chuyển từ chuỗi nhị phân 64 bit thành số float
def bin_to_float64(bin_str):
    int_val = int(bin_str, 2)
    return struct.unpack('>d', int_val.to_bytes(8, byteorder='big'))[0]

# Đọc cây quyết định từ file .mif
# Đọc cây quyết định từ file .mif
def load_tree_from_mif(mif_path):
    records = []
    with open(mif_path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            if not line or len(line) < 95:
                continue

            node = int(line[0:9], 2)  # Đọc node
            feature_bin = line[9:11]  # Đọc feature (2 bit)
            feature = -1 if feature_bin == '11' else int(feature_bin, 2)  # Feature = 11 -> lá, không cần trỏ tới trái/phải

            threshold_bin = line[11:75]  # Đọc threshold (64 bit)
            threshold = bin_to_float64(threshold_bin)

            left_child = int(line[75:84], 2)  # Đọc left child
            right_child = int(line[84:93], 2)  # Đọc right child

            prediction_bin = line[93:95]  # Đọc phần prediction (2 bit)
            if prediction_bin == '11':
                prediction = -1
            elif prediction_bin == '01':
                prediction = 1
            else:
                prediction = 0

            # Nếu feature = 11, thì không cần trỏ tới Left/Right mà trả về trực tiếp Prediction
            records.append({
                'Node': node,
                'Feature': feature,
                'Threshold': threshold,
                'Left_Child': left_child,
                'Right_Child': right_child,
                'Prediction': prediction
            })

    return pd.DataFrame(records)


# Dự đoán từ cây
# Dự đoán từ cây
# Dự đoán từ cây
def predict_from_tree(tree_df, input_data, verbose=False):
    node = 0
    visited_nodes = set()  # Set để lưu các node đã duyệt
    path = []  # Lưu trữ đường đi của các node đã duyệt

    while True:
        if node in visited_nodes:
            # Lỗi vòng lặp vô hạn
            if verbose:
                print(f"❌ Vòng lặp vô hạn phát hiện: đã ghé node {node} trước đó.")
                print("🔍 Đường đi trước khi lỗi xảy ra:")
                for n in path:
                    print(f"  - Node {n}")
            return None
        visited_nodes.add(node)
        path.append(node)

        matches = tree_df[tree_df['Node'] == node]
        if matches.empty:
            if verbose:
                print(f"❌ Node {node} không tồn tại.")
            return None
        row = matches.iloc[0]
        feature = row['Feature']

        # Nếu feature = 11, trả về prediction ngay mà không cần kiểm tra con trái hay phải
        if feature == 11:
            prediction = row['Prediction']
            if verbose:
                print(f"✅ Node {node} là node lá với Feature = 11. Prediction = {prediction}")
            return int(prediction)

        is_leaf = feature == -1
        feature_name = None if is_leaf else feature_index_to_name.get(int(feature), None)

        if is_leaf:
            if verbose:
                print(f"✅ Node {node} là node lá. Prediction = {row['Prediction']}")
            return int(row['Prediction'])

        threshold = float(row['Threshold'])
        if feature_name is not None:
            feature_value = input_data.get(feature_name)

            # Ép kiểu nếu cần
            try:
                if feature_name == 'arbitration_id':
                    if isinstance(feature_value, str):
                        feature_value = int(feature_value, 16)

                elif feature_name == 'timestamp':
                    feature_value = float(feature_value)

                elif feature_name == 'data_field':
                    feature_value = int(feature_value, 16)

            except Exception as e:
                if verbose:
                    print(f"❌ Lỗi khi ép kiểu feature '{feature_name}': {e}")
                return None

            if verbose:
                print(f"🧠 Node {node}: {feature_name} ({feature_value}) "
                      f"{'<= ' if feature_value <= threshold else '>  '} {threshold}")

            if feature_value <= threshold:
                node = int(row['Left_Child'])
            else:
                node = int(row['Right_Child'])



# Bỏ phiếu giữa các cây
def vote_predictions(trees, input_data, verbose=False):
    predictions = []
    for tree_path in trees:
        print(f"\n📁 Đang xử lý: {tree_path}")
        tree_df = load_tree_from_mif(tree_path)
        pred = predict_from_tree(tree_df, input_data, verbose=verbose)
        predictions.append(pred)

    prediction_counts = Counter(predictions)
    voted_prediction = prediction_counts.most_common(1)[0][0]
    return voted_prediction, prediction_counts

# Main test
if __name__ == "__main__":
    trees = [f"LUT/tree_{i}_output.mif" for i in range(21)]
    sample_input = {
        'timestamp': 1672531286.901432,
        'arbitration_id': '0C1',  # Giá trị hex ví dụ
        'data_field': "0000000000000000"  # Giá trị hex ví dụ
    }

    voted_prediction, prediction_counts = vote_predictions(trees, sample_input, verbose=True)
    print(f"\n🧾 Final Voted Prediction: {voted_prediction} (0: Normal, 1: Attack)")
    print(f"Votes: {prediction_counts}")
    print(f"Total Trees: {len(trees)}")
