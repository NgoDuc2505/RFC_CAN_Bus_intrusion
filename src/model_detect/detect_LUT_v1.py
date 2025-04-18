import pandas as pd
from collections import Counter

# Ánh xạ chỉ số feature sang tên cột
feature_index_to_name = {
    '00': "timestamp",
    '01': 'arbitration_id',
    '10': 'data_field',
    '-1': 'None'
}

def convert_timestamp(ts):
    try:
        return float(ts)
    except:
        return 0.0


def preprocess_data(df):
    df = df.copy()
    df['timestamp'] = df['timestamp'].apply(convert_timestamp)
    for col in ['arbitration_id', 'data_field']:
        if df[col].dtype == object:
            df[col] = df[col].apply(lambda x: int(x, 16) if isinstance(x, str) else x)
    return df

def preprocess_data_dict(data_dict):
    data_dict = data_dict.copy()
    data_dict['timestamp'] = convert_timestamp(data_dict['timestamp'])
    for col in ['arbitration_id', 'data_field']:
        if isinstance(data_dict[col], str):
            data_dict[col] = int(data_dict[col], 16)
            # if data_dict[col].dtype == object:
            #     data_dict[col] = data_dict[col].apply(lambda x: int(x, 16) if isinstance(x, str) else x)
    return data_dict

# Hàm đọc LUT từ file CSV
def load_tree_from_csv(csv_path):
    df = pd.read_csv(csv_path)
    df = preprocess_data(df)  # Tiền xử lý dữ liệu
    df.columns = df.columns.str.strip()  # Xóa khoảng trắng
    return df

# Hàm dự đoán giống random forest dựa trên cây
def predict_from_tree(tree_df, input_data, verbose=False):
    node = 0
    while True:
        # matches = tree_df[tree_df['Node'] == node]
        matches = tree_df['Node'] == node
        if matches.empty:
            if verbose:
                print(f"❌ Node {node} không tồn tại.")
            return None
        row = matches.iloc[0]
        
        # Kiểm tra nếu là nút lá (Feature là NaN hoặc -1)
        is_leaf = pd.isna(row['Feature']) or row['Feature'] == -1
        # is_leaf = row['Feature'] == -1
        feature_name = None if is_leaf else feature_index_to_name.get(row['Feature'], None)
        
        if is_leaf:
            # Nếu là nút lá, trả về prediction
            if verbose:
                print(f"✅ Node {node} là node lá. Prediction = {row['Prediction']}")
            return row['Prediction']

        # Nếu không phải nút lá, tiếp tục so sánh
        threshold = row['Threshold']   # Fixed-point Q12.20
        if feature_name is not None:
            feature_value = input_data.get(feature_name)
            if feature_value is None:
                if verbose:
                    print(f"❌ Feature '{feature_name}' không tồn tại trong input.")
                return None

            if verbose:
                print(f"🧠 Node {node}: {feature_name} ({feature_value}) "
                      f"{'<= ' if feature_value <= threshold else '>  '} {threshold}")

            if feature_value <= threshold:
                node = row['Left_Child']
            else:
                node = row['Right_Child']


# Hàm thực hiện voting từ các cây
def vote_predictions(trees, input_data, verbose=False):
    predictions = []
    input_data = preprocess_data_dict(input_data)  # Tiền xử lý dữ liệu đầu vào
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
    trees = [f"src/LUT/tree_{i}.csv" for i in range(21)]

    # Dữ liệu đầu vào
    sample_input_0 = {
        'timestamp': 1672531200, 'arbitration_id': '191', 'data_field': "8409A80D004108",
    }

    sample_input_1 = {
         'timestamp': 1672531286.901432, 'arbitration_id': '0C1', 'data_field': "0000000000000000",
    }
    # Thực hiện voting và lấy kết quả
    voted_prediction, prediction_counts = vote_predictions(trees, sample_input_0, verbose=True)
    
    # Hiển thị kết quả
    print(f"\n🧾 Final Voted Prediction: {voted_prediction} (0: Normal, 1: Attack)")
    print(f"Votes: {prediction_counts}")

