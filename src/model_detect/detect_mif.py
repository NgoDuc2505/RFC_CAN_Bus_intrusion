import pandas as pd
from collections import Counter

# Ánh xạ từ feature index sang tên
feature_index_to_name = {
    0: 'timestamp',
    1: 'arbitration_id',
    10: 'data_field',
    -1: 'none'
}

def parse_mif_line(hex_line):
    # Phân tích một dòng trong file MIF
    node = int(hex_line[0:3], 16)  # Node (3 hex digits)
    feature = int(hex_line[4:5], 16)  # Feature (1 hex digit)
    threshold = int(hex_line[6:22], 16)  # Threshold (16 hex digits)

    # Kiểm tra nếu chuỗi rỗng thì bỏ qua dòng này
    left_child_str = hex_line[23:26]
    if not left_child_str.strip():  # Kiểm tra chuỗi rỗng hoặc chỉ chứa ký tự trắng
        left_child = None
    else:
        left_child = int(left_child_str, 16)

    # Kiểm tra nếu chuỗi rỗng thì bỏ qua dòng này
    right_child_str = hex_line[27:30]
    if not right_child_str.strip():  # Kiểm tra chuỗi rỗng hoặc chỉ chứa ký tự trắng
        right_child = None
    else:
        right_child = int(right_child_str, 16)

    # Kiểm tra nếu chuỗi rỗng thì bỏ qua dòng này
    prediction_str = hex_line[31:32]
    if not prediction_str.strip():  # Kiểm tra chuỗi rỗng hoặc chỉ chứa ký tự trắng
        prediction = None
    else:
        prediction = int(prediction_str, 16)

    # Đổi feature và prediction nếu giá trị bằng 3
    feature = -1 if feature == 3 else feature
    prediction = -1 if prediction == 3 else prediction

    # Tránh chuyển đổi None thành int
    if left_child is None:
        left_child = 0  # Hoặc giá trị mặc định khác nếu cần

    if right_child is None:
        right_child = 0  # Hoặc giá trị mặc định khác nếu cần

    if prediction is None:
        prediction = 0  # Hoặc giá trị mặc định khác nếu cần

    return {
        'Node': node,
        'Feature': feature,
        'Threshold': threshold,
        'Left_Child': left_child,
        'Right_Child': right_child,
        'Prediction': prediction
    }

def load_tree_from_mif(mif_path):
    rows = []
    with open(mif_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('--') or ':' in line:
                continue
            row = parse_mif_line(line)
            rows.append(row)
    return pd.DataFrame(rows)

def predict_from_tree(tree_df, input_data):
    """
    Hàm dự đoán đầu ra của cây quyết định dựa trên dữ liệu đầu vào.
    
    :param tree_df: DataFrame chứa các thông tin cây quyết định.
    :param input_data: Dữ liệu đầu vào để dự đoán.
    :return: Dự đoán từ cây quyết định.
    """
    node = tree_df.iloc[0]  # Lấy dòng đầu tiên làm ví dụ, bạn có thể tùy chỉnh
    while node['Left_Child'] != 0 or node['Right_Child'] != 0:  # Kiểm tra đến khi gặp nút lá
        if input_data[node['Feature']] <= node['Threshold']:
            node = tree_df.loc[tree_df['Node'] == node['Left_Child']].iloc[0]
        else:
            node = tree_df.loc[tree_df['Node'] == node['Right_Child']].iloc[0]

    return node['Prediction']  # Trả về dự đoán cuối cùng

def vote_predictions(trees, input_data):
    predictions = []
    for tree_path in trees:
        tree_df = load_tree_from_mif(tree_path)
        pred = predict_from_tree(tree_df, input_data)
        predictions.append(pred)

    prediction_counts = Counter(predictions)
    voted_prediction = prediction_counts.most_common(1)[0][0]
    return voted_prediction, prediction_counts

def convert_input_to_hex(input_data):
    result = {}

    # timestamp
    timestamp = float(input_data['timestamp'])
    timestamp_scaled = int(timestamp * 1e17)
    result['timestamp'] = format(timestamp_scaled, '016X')

    # arbitration_id
    arbitration_id = input_data['arbitration_id']
    arbitration_id_int = int(arbitration_id, 16)
    result['arbitration_id'] = format(arbitration_id_int, '016X')

    # data_field
    data_field = input_data['data_field']
    data_field_int = int(data_field, 16)
    result['data_field'] = format(data_field_int, '016X')

    return result

if __name__ == "__main__":
    # Cung cấp danh sách các cây quyết định (ví dụ, 21 cây quyết định)
    trees = [f"LUT/tree_{i}_output.mif" for i in range(21)]

    # Mẫu dữ liệu đầu vào
    input_data_list = [
        {'timestamp': 1672531250.218442, 'arbitration_id': '0AA', 'data_field': '0000000000000000'},
        {'timestamp': 1672531250.219211, 'arbitration_id': '0AA', 'data_field': '0000000000000000'},
        {'timestamp': 1672531250.219942, 'arbitration_id': '0AA', 'data_field': '0000000000000000'},
        {'timestamp': 1672531250.220705, 'arbitration_id': '0AA', 'data_field': '0000000000000000'}
    ]

    # Chạy dự đoán cho mỗi input
    for idx, input_data in enumerate(input_data_list):
        print(f"\n🔍 Dự đoán cho input {idx + 1}:")
        hex_input = convert_input_to_hex(input_data)
        for k, v in hex_input.items():
            print(f"  {k:>15}: {v}")

        voted_prediction, prediction_counts = vote_predictions(trees, input_data)

        # Hiển thị kết quả voting
        print(f"🧾 Final Voted Prediction: {voted_prediction} (0: Normal, 1: Attack)")
        print(f"Votes: {prediction_counts}")
