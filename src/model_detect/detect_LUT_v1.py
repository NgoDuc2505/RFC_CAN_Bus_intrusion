import pandas as pd
from collections import Counter

# Ánh xạ chỉ số feature sang tên cột
feature_index_to_name = {
    0: 'arbitration_id',
    1: 'inter_arrival_time',
    10: 'data_entropy',
    11: 'dls',
    -1:'none'
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
        
        # Kiểm tra nếu là nút lá (Feature là NaN hoặc -1)
        is_leaf = pd.isna(row['Feature']) or row['Feature'] == -1
        feature_name = None if is_leaf else feature_index_to_name.get(row['Feature'], "-1")
        
        if is_leaf:
            # Nếu là nút lá, trả về prediction
            if verbose:
                print(f"✅ Node {node} là node lá. Prediction = {row['Prediction']}")
            return row['Prediction']

        # Nếu không phải nút lá, tiếp tục so sánh
        threshold = row['Threshold']   # Fixed-point Q12.20
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
        print(f"\n=>{tree_path}")
        pred = predict_from_tree(tree_df, input_data, verbose=verbose)
        predictions.append(pred)

    # Thực hiện voting (bỏ phiếu), nếu phiếu 0 nhiều hơn, dự đoán là 0, ngược lại là 1
    prediction_counts = Counter(predictions)
    voted_prediction = prediction_counts.most_common(1)[0][0]  # Lấy dự đoán phổ biến nhất

    return voted_prediction, prediction_counts

# Main chạy như bạn yêu cầu
if __name__ == "__main__":
    # Các cây mà bạn muốn dự đoán (tree_0 đến tree_16)
    trees = [f"src/LUT/tree_{i}.csv" for i in range(49)]

    # Dữ liệu đầu vào
    sample_input = {
   'arbitration_id': 882, 'inter_arrival_time': 0.099141, 'data_entropy': 0.54356, 'dls': 8
    }
    # Thực hiện voting và lấy kết quả
    voted_prediction, prediction_counts = vote_predictions(trees, sample_input, verbose=True)
    
    # Hiển thị kết quả
    print(f"\n🧾 Final Voted Prediction: {voted_prediction} (0: Normal, 1: Attack)")
    print(f"Votes: {prediction_counts}")
