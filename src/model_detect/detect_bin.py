# detect_LUT_bin.py
import pickle
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
        tree_df = load_tree_from_bin(tree_path)
        pred = predict_from_tree(tree_df, input_data, verbose=verbose)
        predictions.append(pred)

    prediction_counts = Counter(predictions)
    voted_prediction = prediction_counts.most_common(1)[0][0]
    return voted_prediction, prediction_counts

if __name__ == "__main__":
    trees = [f"src/LUT/tree_{i}.bin" for i in range(21)]
    sample_input = {
        'timestamp': 1672531286.901432,
        'arbitration_id': '0C1',
        'data_field': "0000000000000000"
    }

    sample_input_0 = {
        'timestamp': 1672531200, 'arbitration_id': '191', 'data_field': "8409A80D004108",
    }

    voted_prediction, prediction_counts = vote_predictions(trees, sample_input_0, verbose=True)
    print(f"\n🧾 Final Voted Prediction: {voted_prediction} (0: Normal, 1: Attack)")
    print(f"Votes: {prediction_counts}")
