import pickle
import pandas as pd
from collections import Counter
import time

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

def predict_from_tree(tree_df, input_data):
    node = 0
    while True:
        matches = tree_df[tree_df['Node'] == node]
        if matches.empty:
            return None
        row = matches.iloc[0]
        is_leaf = row['Feature'] == -1
        feature_name = None if is_leaf else feature_index_to_name.get(int(row['Feature']), None)

        if is_leaf:
            return int(row['Prediction'])

        threshold = float(row['Threshold'])
        if feature_name is not None:
            feature_value = input_data.get(feature_name)

            try:
                if feature_name == 'arbitration_id':
                    if isinstance(feature_value, str):
                        feature_value = int(feature_value, 16)
                elif feature_name == 'timestamp':
                    feature_value = float(feature_value)
                elif feature_name == 'data_field':
                    feature_value = int(feature_value, 16)
            except:
                return None

            if feature_value <= threshold:
                node = int(row['Left_Child'])
            else:
                node = int(row['Right_Child'])

def vote_predictions(trees, input_data):
    predictions = []
    for tree_path in trees:
        tree_df = load_tree_from_bin(tree_path)
        pred = predict_from_tree(tree_df, input_data)
        predictions.append(pred)

    prediction_counts = Counter(predictions)
    voted_prediction = prediction_counts.most_common(1)[0][0]
    return voted_prediction, prediction_counts

def evaluate_on_csv(csv_path, trees):
    df = pd.read_csv(csv_path)
    total = len(df)
    correct = 0
    wrong = 0
    times = []

    for index, row in df.iterrows():
        input_data = {
            'timestamp': row['timestamp'],
            'arbitration_id': str(row['arbitration_id']),
            'data_field': row['data_field']
        }
        true_label = int(row['attack'])

        start = time.time()
        pred, _ = vote_predictions(trees, input_data)
        end = time.time()

        elapsed = end - start
        times.append(elapsed)

        if pred == true_label:
            correct += 1
        else:
            wrong += 1

    accuracy = correct / total * 100
    max_time = max(times)
    min_time = min(times)
    avg_time = sum(times) / len(times)

    print(f"\n🔍 ĐÁNH GIÁ MÔ HÌNH")
    print(f"✅ Đúng : {correct} / {total}")
    print(f"❌ Sai  : {wrong} / {total}")
    print(f"🎯 Accuracy: {accuracy:.2f}%")

    print(f"\n⏱️ THỐNG KÊ THỜI GIAN PREDICTION")
    print(f"🔸 Max time: {max_time:.6f} s")
    print(f"🔹 Min time: {min_time:.6f} s")
    print(f"🔺 Avg time: {avg_time:.6f} s")

if __name__ == "__main__":
    trees = [f"src/LUT/tree_{i}.bin" for i in range(21)]

    csv_path = "src/datasets_release/sample_1.csv"
    evaluate_on_csv(csv_path, trees)
