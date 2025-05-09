import os
import glob
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
            line = line.strip()
            if line:
                try:
                    node = int(line[0:9], 2)
                    feature = int(line[9:11], 2)
                    threshold = int(line[11:75], 2)
                    left_child = int(line[75:84], 2)
                    right_child = int(line[84:93], 2)
                    prediction = int(line[93:95], 2)
                    
                    tree_data.append({
                        'Node': node,
                        'Feature': feature,
                        'Threshold': threshold,
                        'Left_Child': left_child,
                        'Right_Child': right_child,
                        'Prediction': prediction
                    })
                except Exception as e:
                    print(f"❌ Lỗi khi phân tích dòng: {line} -> {e}")
                    continue

    tree_df = pd.DataFrame(tree_data)
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

def vote_predictions(tree_paths, input_data, verbose=False):
    predictions = []
    for tree_path in tree_paths:
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
    # Duyệt tất cả file tree*.mif trong thư mục src/LUT/
    tree_folder = "src/LUT"
    tree_paths = sorted(glob.glob(os.path.join(tree_folder, "tree*.mif")))

    if not tree_paths:
        print("❌ Không tìm thấy file .mif nào trong thư mục.")
    else:
        print(f"✅ Đã tìm thấy {len(tree_paths)} cây quyết định.")

        sample_input = {
            'timestamp': 1672531286.901432,
            'arbitration_id': '0C1',
            'data_field': "0000000000000000"
        }

        # Có thể thử nhiều bộ test khác nhau
        voted_prediction, prediction_counts = vote_predictions(tree_paths, sample_input, verbose=True)
        if voted_prediction is not None:
            print(f"\n🧾 Final Voted Prediction: {voted_prediction} (0: Normal, 1: Attack)")
            print(f"Votes: {prediction_counts}")
            print(f"Total Trees: {len(tree_paths)}")
        else:
            print("❌ Không thể đưa ra dự đoán.")
