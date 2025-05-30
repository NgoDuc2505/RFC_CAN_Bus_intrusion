import pandas as pd
import joblib


def load_model(model_path):
    return joblib.load(model_path)


def predict(model, input_data):
    df = pd.DataFrame([input_data])
    prediction = model.predict(df)
    probability = model.predict_proba(df)
    return prediction[0], probability[0]


def load_forest_from_multiple_hex(hex_files):
    forest = {}
    node_counters = {}  
    
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
                
            
            tree = line[:2]
            feature = line[2:4]
            threshold = line[4:12]
            left_child = line[12:14]
            right_child = line[14:16]
            prediction = line[16:18]
            
            if tree not in forest:
                forest[tree] = {}
                node_counters[tree] = 0
                
            node_id = f"{node_counters[tree]:02X}"
            node_counters[tree] += 1
            
            forest[tree][node_id] = {
                'feature': feature,
                'threshold': threshold,
                'left': left_child,
                'right': right_child,
                'prediction': prediction
            }
    
    return forest


def predict_tree(tree, input_dict):
    current_node = '00'

    while True:
        node = tree.get(current_node)
        if not node:
            return None

        if node['feature'] == 'FF':  
            if node['prediction'] != 'FF':
                return int(node['prediction'], 16)
            else:
                return None

        feature_map = {
            '00': 'arbitration_id',
            '01': 'inter_arrival_time',
            '10': 'data_entropy',
            '11': 'dls'
        }

        feature_key = feature_map.get(node['feature'], None)
        if feature_key is None:
            return None

        threshold_hex = node['threshold']
        if threshold_hex == 'FF':
            return None

        if feature_key in ['inter_arrival_time', 'data_entropy']:
            threshold = int(threshold_hex, 16) / float(1 << 24)
        else:
            threshold = int(threshold_hex, 16)

        value = input_dict.get(feature_key, 0)

        if value <= threshold:
            current_node = node['left']
        else:
            current_node = node['right']


def predict_forest(forest, input_dict):
    vote_counts = {}

    for tree_id, tree in forest.items():
        pred = predict_tree(tree, input_dict)
        print(f"Tree {tree_id}: Prediction: {pred}")
        if pred is not None:
            if pred not in vote_counts:
                vote_counts[pred] = 1
            else:
                vote_counts[pred] += 1

    max_votes = -1
    final_pred = None
    for label, count in vote_counts.items():
        if count > max_votes:
            max_votes = count
            final_pred = label
    print(f"Votes: {vote_counts}")
    return final_pred


if __name__ == "__main__":
    file_path = 'split_model_v4_v2\LUTModel_hex.hex'  

    model_path = "random_forest_model_v4_lite_17ts.pkl"
    model = load_model(model_path)

    sample_input_3 = {
        'arbitration_id': 1838,            
        'inter_arrival_time': 0.001,       
        'data_entropy': 0.09,              
        'dls': 1                          
    }

    # Tải forest từ nhiều file .hex
    forest = load_forest_from_multiple_hex(hex_files)
    
    # Dự đoán bằng voting
    prediction = predict_forest(forest, sample_input_3)
    
    # Dự đoán bằng mô hình joblib
    pred, prob = predict(model, sample_input_3)
    print(f"Prediction (sklearn): {pred} (0: Normal, 1: Attack)")
    print(f"Probability: {prob}")
    
    if prediction == 1:
        print("Voting prediction: Tấn công")
    elif prediction == 0:
        print("Voting prediction: Bình thường")
    else:
        print("Không xác định nhãn.")
