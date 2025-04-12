import pandas as pd
import joblib


def load_model(model_path):
    return joblib.load(model_path)

def predict(model, input_data):
    df = pd.DataFrame([input_data])
    prediction = model.predict(df)
    probability = model.predict_proba(df)
    return prediction[0], probability[0]

def load_forest_from_csv(file_path):
    df = pd.read_csv(file_path)
    forest = {}

    for _, row in df.iterrows():
        tree_id = row['Tree']
        node_id = row['Node']
        feature = row['Feature']
        threshold = row['Threshold']
        left = row['Left_Child']
        right = row['Right_Child']
        prediction = row['Prediction']

        if tree_id not in forest:
            forest[tree_id] = {}

        forest[tree_id][node_id] = {
            'feature': feature,
            'threshold': threshold,
            'left': left,
            'right': right,
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
    file_path = 'random_forest_model_v4_optimized_LUT_mem.csv'  

    model_path = "random_forest_model_v4_optimized.pkl"
    model = load_model(model_path)

    sample_input = {
        'arbitration_id': 342,
        'inter_arrival_time': 0.0,
        'data_entropy': 1.061,
        'dls': 8,
    }

    sample_input_2 = {
        'arbitration_id': 977,
        'inter_arrival_time': 0.02,
        'data_entropy': 1.549,
        'dls': 8,
    }

    sample_input_3 = {
        'arbitration_id': 1838,            
        'inter_arrival_time': 0.001,       
        'data_entropy': 0.09,              
        'dls': 1                          
    }

    forest = load_forest_from_csv(file_path)
    prediction = predict_forest(forest, sample_input_3)
    pred, prob = predict(model, sample_input_3)
    print(f"Prediction: {pred} (0: Normal, 1: Attack)")
    print(f"Probability: {prob}")
    if prediction == 1:
        print("Dự đoán: Tấn công")
    elif prediction == 0:
        print("Dự đoán: Bình thường")
    else:
        print("Không xác định nhãn.")
