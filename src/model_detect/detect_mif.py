# mif_parser_95bit_verbose.py
import os
from collections import Counter

def parse_binary_row_95bit(bin_str):
    assert len(bin_str) == 95, "Dòng nhị phân phải đúng 95 bit"

    node        = int(bin_str[0:9], 2)
    feature_bin = bin_str[9:11]
    feature     = int(feature_bin, 2)
    if feature_bin == '11':
        feature = -1  # node lá

    threshold   = int(bin_str[11:75], 2)
    left_child  = int(bin_str[75:84], 2)
    right_child = int(bin_str[84:93], 2)
    prediction  = bin_str[93:95]  # chuỗi nhị phân

    prediction_val = {'00': 0, '01': 1, '11': -1}.get(prediction, None)

    return {
        'Node': node,
        'Feature': feature,
        'Threshold': threshold,
        'Left_Child': left_child,
        'Right_Child': right_child,
        'Prediction': prediction_val
    }

def load_tree_from_mif(mif_path):
    with open(mif_path, 'r') as f:
        lines = f.readlines()
    
    # Lọc dòng nhị phân 95 bit
    data_lines = [line.strip() for line in lines
                  if set(line.strip()) <= {'0', '1'} and len(line.strip()) == 95]

    rows = [parse_binary_row_95bit(line) for line in data_lines]
    return rows

def predict_from_parsed_tree(tree_rows, input_data, verbose=False):
    node = 0
    # Chuẩn bị chuỗi nhị phân đầu vào
    input_bin = {
        'timestamp':      format(int(float(input_data['timestamp'])), '064b'),
        'arbitration_id': format(int(input_data['arbitration_id'], 16), '064b'),
        'data_field':     format(int(input_data['data_field'], 16), '064b')
    }

    while True:
        current = next((row for row in tree_rows if row['Node'] == node), None)
        if current is None:
            print(f"❌ Node {node} không tồn tại.")
            return None

        # Nếu là leaf node
        if current['Feature'] == -1:
            if verbose:
                print(f"Node {node} là lá → Prediction = {current['Prediction']}")
            return current['Prediction']

        # Xác định feature name
        feature_name = {0: 'timestamp', 1: 'arbitration_id', 2: 'data_field'}[current['Feature']]

        # Lấy string nhị phân của threshold và input
        threshold_bin  = format(current['Threshold'], '064b')
        input_value_bin = input_bin[feature_name]

        # In thông tin so sánh
        if verbose:
            print(f"\n-- Node {node} --")
            print(f" Feature       : {feature_name} (code = {current['Feature']:02b})")
            print(f" Input bits    : {input_value_bin}")
            print(f" Threshold bits: {threshold_bin}")
            cmp = "<=" if input_value_bin <= threshold_bin else " >"
            print(f" So sánh: {input_value_bin} {cmp} {threshold_bin}")

        # Chọn nhánh
        if input_value_bin <= threshold_bin:
            node = current['Left_Child']
            if verbose:
                print(f" → Chọn Left_Child = {node}")
        else:
            node = current['Right_Child']
            if verbose:
                print(f" → Chọn Right_Child = {node}")

def vote_predictions_mif(trees, input_data, verbose=False):
    predictions = []
    for tree_path in trees:
        print(f"\n📁 Đang xử lý cây: {tree_path}")
        tree = load_tree_from_mif(tree_path)
        pred = predict_from_parsed_tree(tree, input_data, verbose=verbose)
        predictions.append(pred)

    counts = Counter(predictions)
    voted = counts.most_common(1)[0][0]
    return voted, counts

if __name__ == "__main__":
    trees = [f"src/LUT/tree_{i}_v.mif" for i in range(21)]
    sample_input = {
 'timestamp': 1672531251.000602, 'arbitration_id': '0AA', 'data_field': "0000000000000000",
    }

    sample_input_1= {
    'timestamp': 1672531286.901432,
    'arbitration_id': '0C1',
    'data_field': "0000000000000000"
    }

    sample_input_0 = {
    'timestamp': 1672531398.7673929, 'arbitration_id': '3E9', 'data_field': "1B4C05111B511C69",
    }

    voted_pred, pred_counts = vote_predictions_mif(trees, sample_input_0, verbose=True)
    print(f"\n🧾 Final Voted Prediction: {voted_pred} (0: Normal, 1: Attack)")
    print(f"Votes: {pred_counts}")
