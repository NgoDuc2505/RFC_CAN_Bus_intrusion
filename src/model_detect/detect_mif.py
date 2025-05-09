import pandas as pd
from collections import Counter

# Ánh xạ chỉ số feature sang tên cột
feature_index_to_name = {
    0: 'timestamp',
    1: 'arbitration_id',
    10: 'data_field',
    -1: 'none'
}
def load_tree_from_mif(mif_path):
    tree_data = []
    with open(mif_path, mode='r') as miffile:
        for line in miffile:
            line = line.strip()  # Loại bỏ khoảng trắng thừa
            if line:
                try:
                    # Đọc các phần tử từ dòng nhị phân theo đúng số bit đã cho:
                    node = int(line[0:9], 2)  # 9 bit cho Node
                    feature = int(line[9:11], 2)  # 2 bit cho Feature
                    threshold = int(line[11:75], 2)  # 64 bit cho Threshold
                    left_child = int(line[75:84], 2)  # 9 bit cho Left Child
                    right_child = int(line[84:93], 2)  # 9 bit cho Right Child
                    prediction = int(line[93:95], 2)  # 2 bit cho Prediction
                    
                    # Thêm dữ liệu vào danh sách
                    tree_data.append({
                        'Node': node,
                        'Feature': feature,
                        'Threshold': threshold,
                        'Left_Child': left_child,
                        'Right_Child': right_child,
                        'Prediction': prediction
                    })
                except Exception as e:
                    print(f"❌ Lỗi khi phân tích cú pháp dòng: {line} -> {e}")
                    continue  # Bỏ qua dòng bị lỗi và tiếp tục xử lý các dòng khác

    # Tạo DataFrame từ dữ liệu đã đọc
    tree_df = pd.DataFrame(tree_data)
    
    # In ra các cột và phần tử để kiểm tra
    print(f"✅ Đã tải dữ liệu từ {mif_path}. Các cột: {tree_df.columns}")
    print(tree_df.head())  # In ra 5 dòng đầu tiên để kiểm tra dữ liệu
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
        is_leaf = pd.isna(row['Feature']) or row['Feature'] == -1
        feature_name = None if is_leaf else feature_index_to_name.get(int(row['Feature']), None)

        if is_leaf:
            if verbose:
                print(f"✅ Node {node} là node lá. Prediction = {row['Prediction']}")
            return int(row['Prediction'])

        threshold = row['Threshold']
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
                node = row['Left_Child']
            else:
                node = row['Right_Child']

def vote_predictions(trees, input_data, verbose=False):
    predictions = []
    for tree_path in trees:
        print(f"\n📁 Đang xử lý: {tree_path}")
        tree_df = load_tree_from_mif(tree_path)
        pred = predict_from_tree(tree_df, input_data, verbose=verbose)
        if pred is not None:
            predictions.append(pred)
        else:
            print(f"❌ Không thể dự đoán với cây {tree_path}")
    
    if not predictions:
        print("❌ Không có dự đoán nào được trả về.")
        return None, None
    
    prediction_counts = Counter(predictions)
    voted_prediction = prediction_counts.most_common(1)[0][0]
    return voted_prediction, prediction_counts

if __name__ == "__main__":
    trees = [f"LUT/tree_{i}_output.mif" for i in range(21)]  # Các file .mif đã tạo từ phần trước
    sample_input = {
        'timestamp': 1672531286.901432,
        'arbitration_id': '0C1',
        'data_field': "0000000000000000"
    }

    sample_input_0 = {
        'timestamp': 1672531398.7673929, 'arbitration_id': '3E9', 'data_field': "1B4C05111B511C69",
    }

    # Thử với dữ liệu đầu vào mẫu
    voted_prediction, prediction_counts = vote_predictions(trees, sample_input, verbose=True)
    if voted_prediction is not None:
        print(f"\n🧾 Final Voted Prediction: {voted_prediction} (0: Normal, 1: Attack)")
        print(f"Votes: {prediction_counts}")
        print(f"Total Trees: {len(trees)}")
    else:
        print("❌ Không thể đưa ra dự đoán.")
