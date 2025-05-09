import os
import math

def parse_mif_line(line):
    bits = line.strip().replace(' ', '')
    if len(bits) != 95:
        return None
    node_id = int(bits[0:9], 2)
    feature_id = int(bits[9:11], 2)
    threshold = int(bits[11:75], 2)
    left = int(bits[75:84], 2)
    right = int(bits[84:93], 2)
    prediction = int(bits[93:95], 2)
    return {
        'node_id': node_id,
        'feature_id': feature_id,
        'threshold': threshold,
        'left': left,
        'right': right,
        'prediction': prediction
    }

def load_tree_mif(filepath):
    tree = {}
    with open(filepath, 'r') as f:
        for line in f:
            if not line.strip() or line.startswith('--') or ':' in line:
                continue
            node = parse_mif_line(line)
            if node:
                tree[node['node_id']] = node
    return tree

def calculate_entropy(hex_data):
    if len(hex_data) % 2 != 0:
        raise ValueError("Hex data không hợp lệ")
    byte_data = bytes.fromhex(hex_data)
    if not byte_data:
        return 0.0
    freq = [0] * 256
    for b in byte_data:
        freq[b] += 1
    entropy = 0.0
    for f in freq:
        if f > 0:
            p = f / len(byte_data)
            entropy -= p * math.log2(p)
    return entropy

def extract_features(sample):
    arbitration_int = int(sample['arbitration_id'], 16)
    entropy = calculate_entropy(sample['data_field'])
    length = len(sample['data_field']) // 2
    return {
        0: arbitration_int,
        1: int(entropy * 1000),
        2: length
    }

def run_tree_prediction(tree_dict, sample_features):
    current_node_id = 0
    while True:
        node = tree_dict.get(current_node_id)
        if node is None:
            raise Exception(f"Không tìm thấy node {current_node_id}")
        if node['left'] == 0 and node['right'] == 0:
            return node['prediction']
        feature_value = sample_features.get(node['feature_id'], 0)
        if feature_value < node['threshold']:
            current_node_id = node['left']
        else:
            current_node_id = node['right']

def run_forest_prediction(folder_path, sample_input):
    features = extract_features(sample_input)
    predictions = []
    for file in os.listdir(folder_path):
        if file.endswith(".mif"):
            path = os.path.join(folder_path, file)
            tree = load_tree_mif(path)
            pred = run_tree_prediction(tree, features)
            predictions.append(pred)
    # Majority vote
    if not predictions:
        raise ValueError("Không tìm thấy cây nào.")
    return round(sum(predictions) / len(predictions)), predictions

# === Example ===
sample_input = {
    'timestamp': 1672531286.901432,
    'arbitration_id': '0C1',
    'data_field': "0000000000000000"
}

sample_input_0 = {
    'timestamp': 1672531398.7673929, 'arbitration_id': '3E9', 'data_field': "1B4C05111B511C69",
}

folder = "src/LUT"  # thay bằng folder chứa file .mif
final_pred, all_preds = run_forest_prediction(folder, sample_input_0)

print(f"Kết quả đa số (majority): {final_pred}")
print(f"Kết quả từng cây: {all_preds}")
