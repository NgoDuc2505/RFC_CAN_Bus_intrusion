import pandas as pd
from collections import Counter

# Ánh xạ chỉ số feature sang tên cột
feature_index_to_name = {
    0: 'arbitration_id',
    1: 'inter_arrival_time',
    10: 'data_entropy',
    11: 'dls',
    -1: 'none'
}

# Hàm đọc LUT từ file CSV
def load_tree_from_csv(csv_path):
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()  # Xóa khoảng trắng
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
        
        is_leaf = pd.isna(row['Feature']) or row['Feature'] == -1
        feature_name = None if is_leaf else feature_index_to_name.get(row['Feature'], "-1")
        
        if is_leaf:
            if verbose:
                print(f"✅ Node {node} là node lá. Prediction = {row['Prediction']}")
            return row['Prediction']

        threshold = row['Threshold']
        feature_value = input_data[feature_name]

        if verbose:
            print(f"🧠 Node {node}: {feature_name} ({feature_value:.5f}) "
                  f"{'<= ' if feature_value <= threshold else '>  '} {threshold}")

        if feature_value <= threshold:
            node = row['Left_Child']
        else:
            node = row['Right_Child']

# Hàm thực hiện voting từ các cây
def vote_predictions(trees, input_data, verbose=False):
    predictions = []
    for tree_path in trees:
        tree_df = load_tree_from_csv(tree_path)
        if verbose:
            print(f"\n=> {tree_path}")
        pred = predict_from_tree(tree_df, input_data, verbose=verbose)
        predictions.append(pred)

    prediction_counts = Counter(predictions)
    voted_prediction = prediction_counts.most_common(1)[0][0]

    return voted_prediction, prediction_counts

# Hàm chạy trên chuỗi frame từ file CSV và lưu kết quả
def run_on_frame_sequence(input_csv_path, output_csv_path, trees, verbose=False):
    df = pd.read_csv(input_csv_path)
    results = []

    for idx, row in df.iterrows():
        input_data = {
            'arbitration_id': row['arbitration_id'],
            'inter_arrival_time': row['inter_arrival_time'],
            'data_entropy': row['data_entropy'],
            'dls': row['dls']
        }

        voted_prediction, prediction_counts = vote_predictions(trees, input_data, verbose=verbose)
        label = 'Attack' if voted_prediction == 1 else 'Normal'

        result_row = row.to_dict()
        result_row['Prediction'] = voted_prediction
        result_row['Label'] = label
        result_row['Votes'] = str(dict(prediction_counts))  # Convert Counter to string

        results.append(result_row)

    pd.DataFrame(results).to_csv(output_csv_path, index=False)
    print(f"\n✅ Đã ghi kết quả vào: {output_csv_path}")

# Chạy chương trình chính
if __name__ == "__main__":
    # Tạo danh sách các cây từ tree_0.csv đến tree_48.csv
    trees = [f"src/LUT/tree_{i}.csv" for i in range(49)]

    # File CSV đầu vào (chuỗi frame) và file kết quả đầu ra
    input_csv = "src/datasets_release/test_01_known_vehicle_known_attack/DoS-3-attack.csv"
    output_csv = "src/datasets_release/test_01_known_vehicle_known_attack/predicted_results_DoS_3.csv"

    # Thực hiện dự đoán trên toàn bộ chuỗi frame
    run_on_frame_sequence(input_csv, output_csv, trees, verbose=False)
