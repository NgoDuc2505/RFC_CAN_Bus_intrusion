# detect_LUT_csv.py
import pandas as pd
from collections import Counter

# Ánh xạ chỉ số feature sang tên cột
feature_index_to_name = {
    0: 'timestamp',
    1: 'arbitration_id',
    10: 'data_field',
    -1: 'none'
}

def load_tree_from_csv(csv_path):
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()
    return df

def predict_from_tree(tree_df, input_data, verbose=False):
    node = 0
    while True:
        matches = tree_df[tree_df['Node'] == node]
        if matches.empty:
            if verbose:
                print(f"❌ Node {node} không tồn tại.")
            return None
        row = matches.iloc[0]
        is_leaf = pd.isna(row['Feature']) or row['Feature'] == -1
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
                    # Tùy logic, bạn có thể ép về int hoặc giữ nguyên string
                    # ví dụ: int từ hex string:
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

def vote_predictions(trees, input_data, verbose=False):
    predictions = []
    for tree_path in trees:
        print(f"\n📁 Đang xử lý: {tree_path}")
        tree_df = load_tree_from_csv(tree_path)
        pred = predict_from_tree(tree_df, input_data, verbose=verbose)
        predictions.append(pred)

    prediction_counts = Counter(predictions)
    voted_prediction = prediction_counts.most_common(1)[0][0]
    return voted_prediction, prediction_counts

if __name__ == "__main__":
    trees = [f"LUT/tree_{i}_v.csv" for i in range(21)]
    sample_input = {
       'timestamp':     1672531250.984151,
        'arbitration_id': '0AA',
        'data_field':     '0000000000000000',
    }

    sample_input_0 = {
        'timestamp': 1672531251.000602, 'arbitration_id': '0AA', 'data_field': "0000000000000000",
    }
    voted_prediction, prediction_counts = vote_predictions(trees, sample_input, verbose=True)
    print(f"\n🧾 Final Voted Prediction: {voted_prediction} (0: Normal, 1: Attack)")
    print(f"Votes: {prediction_counts}")
    print(f"Total Trees: {len(trees)}")