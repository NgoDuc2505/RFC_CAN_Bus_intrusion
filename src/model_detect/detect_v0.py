# detect_LUT_bin.py
import pickle
import pandas as pd
from collections import Counter

feature_index_to_name = {
    0: 'timestamp',
    1: 'arbitration_id',
    10: 'data_field',
    -1: 'none'
}

def load_tree_from_bin(bin_path):
    with open(bin_path, 'rb') as f:
        tree_df = pickle.load(f)
    return tree_df

def predict_from_tree(tree_df, input_data, verbose=False):
    node = 0
    while True:
        matches = tree_df[tree_df['Node'] == node]
        if matches.empty:
            if verbose:
                print(f"❌ Node {node} không tồn tại.")
            return None
        row = matches.iloc[0]
        is_leaf = row['Feature'] == -1
        feature_name = None if is_leaf else feature_index_to_name.get(int(row['Feature']), None)

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

            if feature_value <= threshold:
                node = int(row['Left_Child'])
            else:
                node = int(row['Right_Child'])

def vote_predictions(trees, input_data, verbose=False):
    predictions = []
    for tree_path in trees:
        tree_df = load_tree_from_bin(tree_path)
        pred = predict_from_tree(tree_df, input_data, verbose=verbose)
        predictions.append(pred)

    prediction_counts = Counter(predictions)
    voted_prediction = prediction_counts.most_common(1)[0][0]
    return voted_prediction, prediction_counts

def evaluate_on_csv(csv_path, trees):
    df = pd.read_csv(csv_path)
    total = len(df)
    correct = 0
    wrong = 0

    for index, row in df.iterrows():
        input_data = {
            'timestamp': row['timestamp'],
            'arbitration_id': str(row['arbitration_id']),
            'data_field': row['data_field']
        }
        true_label = int(row['attack'])
        pred, _ = vote_predictions(trees, input_data, verbose=False)

        if pred == true_label:
            correct += 1
        else:
            wrong += 1

    accuracy = correct / total * 100
    print(f"\n🔍 ĐÁNH GIÁ MÔ HÌNH")
    print(f"✅ Đúng : {correct} / {total}")
    print(f"❌ Sai  : {wrong} / {total}")
    print(f"🎯 Accuracy: {accuracy:.2f}%")

if __name__ == "__main__":
    trees = [f"src/LUT/tree_{i}.bin" for i in range(21)]
    
    # Chạy đánh giá toàn bộ dữ liệu trong file CSV
    csv_path = "src/datasets_release/set_03/sample_01_known_vehicle_known_attack/DoS-1.csv"  # 🔁 THAY TÊN FILE TẠI ĐÂY
    evaluate_on_csv(csv_path, trees)
