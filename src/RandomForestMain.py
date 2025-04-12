#===========================ConvertToCSV======================================
import pandas as pd
import numpy as np
from collections import Counter
import glob
import os
from tqdm import tqdm

class CANDataProcessor:
    def __init__(self):
        self.processed_count = 0
        
    def calculate_entropy(self, hex_data):
        """Tính toán entropy cho chuỗi hex"""
        if pd.isna(hex_data) or not isinstance(hex_data, str) or len(hex_data) % 2 != 0:
            return 0.0
        
        try:
            byte_values = [hex_data[i:i+2] for i in range(0, len(hex_data), 2)]
            byte_counts = Counter(byte_values)
            total_bytes = len(byte_values)
            probabilities = [count / total_bytes for count in byte_counts.values()]
            return round(-sum(p * np.log2(p) for p in probabilities if p > 0), 3)
        except Exception:
            return 0.0

    def preprocess_dataframe(self, df):
        """Tiền xử lý dataframe"""
        # Chuyển đổi arbitration_id
        df["arbitration_id"] = df["arbitration_id"].apply(lambda x: int(x, 16) if isinstance(x, str) else x)
        
        # Tính toán thời gian
        df["timestamp"] = pd.to_numeric(df["timestamp"], errors="coerce").fillna(0)
        df["inter_arrival_time"] = df.groupby("arbitration_id")["timestamp"].diff().fillna(0).round(6)
        
        # Thêm đặc trưng thống kê
        df['mean_delta_T'] = df['inter_arrival_time'].mean()
        df['var_delta_T'] = df['inter_arrival_time'].var(ddof=0)
        
        # Tính entropy ID
        id_counts = df['arbitration_id'].value_counts(normalize=True)
        df['entropy_ID'] = -sum(p * np.log2(p) for p in id_counts if p > 0)
        
        # Phát hiện tấn công
        df['flooding_attack'] = (df['inter_arrival_time'] < 0.001).astype(int)
        df['replay_attack'] = df.duplicated(subset=['arbitration_id', 'data_field'], keep=False).astype(int)
        
        # Tính bit flipping rate
        df['bit_flipping_rate'] = df['data_field'].apply(self._calc_bit_flipping).round(4)
        
        return df

    def _calc_bit_flipping(self, x):
        """Hàm helper tính bit flipping rate"""
        if not isinstance(x, str):
            return 0.0
        try:
            bits = sum(bin(int(x[i:i+2], 16)).count('1') for i in range(0, len(x), 2) if x[i:i+2].isalnum())
            return bits / (len(x) * 4)
        except:
            return 0.0

    def process_files(self, file_list, label, output_file, mode='append'):
        """Xử lý danh sách file"""
        if not file_list:
            print(f"[!] Không tìm thấy file cho label {label}")
            return False

        processed_dfs = []
        for file in tqdm(file_list, desc=f"Đang xử lý {'bình thường' if label == 0 else 'tấn công'}"):
            try:
                df = pd.read_csv(file)
                df = self.preprocess_dataframe(df)
                df["data_entropy"] = df["data_field"].apply(self.calculate_entropy)
                df['dls'] = df['data_field'].str.len() // 2
                df['label'] = label  # Gán label (0 cho bình thường, 1 cho tấn công)
                processed_dfs.append(df)
                self.processed_count += len(df)
            except Exception as e:
                print(f"[!] Lỗi khi xử lý {os.path.basename(file)}: {str(e)}")
                continue

        if not processed_dfs:
            print(f"[!] Không có dữ liệu nào được xử lý cho label {label}")
            return False

        result_df = pd.concat(processed_dfs, ignore_index=True)
        final_columns = [
            'arbitration_id', 'inter_arrival_time', 'mean_delta_T', 
            'entropy_ID', 'bit_flipping_rate', 'data_entropy', 'label'
        ]
        result_df = result_df[final_columns]

        if mode == 'append' and os.path.exists(output_file):
            existing_df = pd.read_csv(output_file)
            result_df = pd.concat([existing_df, result_df], ignore_index=True)

        result_df.to_csv(output_file, index=False)
        print(f"[✓] Đã xử lý xong {len(processed_dfs)} file, tổng {len(result_df)} mẫu (label: {label})")
        return True


def main():
    print("=== BẮT ĐẦU XỬ LÝ DỮ LIỆU CAN ===")
    processor = CANDataProcessor()
    
    config = {
        "normal_path": {
            "path": "RFC_CAN_Bus_intrusion/src/su2017/attack-free/*.csv",
            "label": 0  # Label 0 cho dữ liệu bình thường
        },
        "attack_paths": {
            "combined": {
                "path": "RFC_CAN_Bus_intrusion/src/su2017/combined-attacks/*.csv",
                "label": 1  # Label 1 cho tấn công
            },
            "dos": {
                "path": "RFC_CAN_Bus_intrusion/src/su2017/DoS-attacks/*.csv",
                "label": 1
            },
            "fuzzy": {
                "path": "RFC_CAN_Bus_intrusion/src/su2017/fuzzing-attacks/*.csv",
                "label": 1
            },
            "gear": {
                "path": "RFC_CAN_Bus_intrusion/src/su2017/gear-attacks/*.csv",
                "label": 1
            },
            "interval": {
                "path": "RFC_CAN_Bus_intrusion/src/su2017/interval-attacks/*.csv",
                "label": 1
            },
            "rpm": {
                "path": "RFC_CAN_Bus_intrusion/src/su2017/rpmear-attacks/*.csv",
                "label": 1
            },
            "speed": {
                "path": "RFC_CAN_Bus_intrusion/src/su2017/speed-attacks/*.csv",
                "label": 1
            },
            "standstill": {
                "path": "RFC_CAN_Bus_intrusion/src/su2017/standstill-attacks/*.csv",
                "label": 1
            },
            "systematic": {
                "path": "RFC_CAN_Bus_intrusion/src/su2017/systematic-attacks/*.csv",
                "label": 1
            },
        },
        "output_file": "can_data_processed.csv"
    }

    # Xử lý dữ liệu bình thường (label = 0)
    normal_files = glob.glob(config["normal_path"]["path"])
    if normal_files:
        print("\n[+] Đang xử lý dữ liệu bình thường (label=0)...")
        processor.process_files(normal_files, 
                              config["normal_path"]["label"], 
                              config["output_file"], 
                              'overwrite')

    # Xử lý dữ liệu tấn công (label = 1)
    for attack_name, attack_config in config["attack_paths"].items():
        attack_files = glob.glob(attack_config["path"])
        if attack_files:
            print(f"\n[+] Đang xử lý tấn công {attack_name} (label=1)...")
            processor.process_files(attack_files, 
                                  attack_config["label"], 
                                  config["output_file"], 
                                  'append')

    print(f"\n=== HOÀN THÀNH ===\nTổng số mẫu đã xử lý: {processor.processed_count}")
    print(f"Kết quả đã được lưu tại: {config['output_file']}")


if __name__ == "__main__":
    main()





#===================TRAIN AI =======================
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib

def train():
    df = pd.read_csv("RFC_CAN_Bus_intrusion/src/can_data_v7_2.csv")
    X = df.drop(columns=['label'])
    y = df['label']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier(#n_estimators=20,
                                   n_estimators=16,
                                   min_samples_split=2,
                                  #  max_depth= 10,
                                   max_depth= 8,
                                   max_leaf_nodes=30,
                                   random_state=42,
                                   criterion='gini',
                                    n_jobs=-1)
    model.fit(X_train, y_train)

    joblib.dump(model, "random_forest_model_v4_lite.pkl")
    print("Model trained and saved as random_forest_model.pkl")

    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    print(f"Model Accuracy: {accuracy:.4f}")
    print("Classification Report:")
    print(classification_report(y_test, predictions))
    print("Confusion Matrix:")
    print(confusion_matrix(y_test, predictions))
    #print(f"Predictions: {predictions}")

if __name__ == "__main__":
    train()

#====================== Detect =====================
import pandas as pd
import joblib

def load_model(model_path):
    return joblib.load(model_path)

def predict(model, input_data):
    df = pd.DataFrame([input_data])
    prediction = model.predict(df)
    probability = model.predict_proba(df)
    return prediction[0], probability[0]

if __name__ == "__main__":
    model_path = "RFC_CAN_Bus_intrusion/src/random_forest_model_v4_lite.pkl"
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

    pred, prob = predict(model, sample_input_2)
    print(f"Prediction: {pred} (0: Normal, 1: Attack)")
    print(f"Probability: {prob}")


#==================== ConvertLUT ==================
import pickle
import pandas as pd
import numpy as np
from sklearn.tree import _tree
import joblib


def extract_tree_info(tree, tree_id, feature_names, mode="mem"):
    tree_ = tree.tree_
    feature_name = [
        feature_names[i] if i != _tree.TREE_UNDEFINED else "N/A"
        for i in tree_.feature
    ]
    nodes = []

    
    for node_id in range(tree_.node_count):
        node_info = {
            "Tree": tree_id,
            "Node": node_id,
            "Feature": feature_name[node_id],
            "Threshold": tree_.threshold[node_id],
            "Left_Child": tree_.children_left[node_id],
            "Right_Child": tree_.children_right[node_id],
            "Prediction": np.nan  
        }

        if node_info["Feature"] == "N/A":
            node_info["Threshold"] = np.nan
            node_info["Left_Child"] = np.nan
            node_info["Right_Child"] = np.nan
            node_info["Prediction"] = np.argmax(tree_.value[node_id])
        else:
            node_info["Prediction"] = np.nan
        
        if mode == "mem":
            node_info = convertNodeToMemFile(node_info)

        nodes.append(node_info)
    
    return nodes

def convertNodeToMemFile(node_info: dict[str, any]) -> dict[str, any]:
    node_info["Tree"] = f"{int(node_info["Tree"]):02x}"
    node_info["Node"] = f"{int(node_info["Node"]):02x}"
    if(node_info["Feature"] != "N/A"):
        node_info["Threshold"] =  f"{int(float(node_info["Threshold"]) * (2**16)):08x}"
        node_info["Left_Child"] = f"{int(node_info["Left_Child"]):02x}"
        node_info["Right_Child"] = f"{int(node_info["Right_Child"]):02x}"
        node_info["Prediction"] = "FF"
    else:
        node_info["Threshold"] = "FF"
        node_info["Left_Child"] = "FF"
        node_info["Right_Child"] = "FF"
        node_info["Prediction"] = f"{int(node_info["Prediction"]):02x}"
        node_info["Feature"] = "FF"
    return node_info
    


def convert_pkl_to_csv(pkl_path, csv_path, feature_names, mode="mem"):
    
    with open(pkl_path, 'rb') as file:
        model = joblib.load(file)
    
    all_nodes = []
   
    for tree_id, estimator in enumerate(model.estimators_):
        nodes = extract_tree_info(estimator, tree_id, feature_names, mode)
        all_nodes.extend(nodes)
    

    df = pd.DataFrame(all_nodes)
    
    # Định dạng lại cột
    # df["Threshold"] = df["Threshold"].apply(lambda x: f"{x:.6f}" if not np.isnan(x) else "N/A")
    # df["Left_Child"] = df["Left_Child"].apply(lambda x: int(x) if not np.isnan(x) else "N/A")
    # df["Right_Child"] = df["Right_Child"].apply(lambda x: int(x) if not np.isnan(x) else "N/A")
    # df["Prediction"] = df["Prediction"].apply(lambda x: int(x) if not np.isnan(x) else "N/A")
    
    # Sắp xếp cột theo yêu cầu
    df = df[["Tree", "Node", "Feature", "Threshold", "Left_Child", "Right_Child", "Prediction"]]
    
    # Lưu vào .csv
    df.to_csv(csv_path, index=False)
    print(f"Đã lưu file .csv vào {csv_path}")


if __name__ == "__main__":
    feature_names =         ["A_ID", "T_A", "D_E", "DLS"]
    feature_names_mapping = ["00", "01", "10", "11"]
    pkl_file = "random_forest_model_v4_optimized.pkl"  
    csv_file = "random_forest_model_v4_optimized_LUT_mem.csv"      
    
    
    convert_pkl_to_csv(pkl_file, csv_file, feature_names_mapping, mode="mem")

#======================== ConvertHEX ========================
import csv

# Danh sách file đầu vào
input_files = [
    'src/LUT/split_model_v4_00.csv',
    'src/LUT/split_model_v4_01.csv',
    'src/LUT/split_model_v4_10.csv'
]

output_file = 'src/LUT/merged_model.hex'
offset = 0
all_lines = []

for file in input_files:
    with open(file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        lines = []
        for row in reader:
            feature     = format(int(row['Feature'], 16), '02X')
            threshold   = format(int(row['Threshold'], 16), '08X')
            left_child  = format(int(row['Left_Child'], 16) + offset, '02X') if row['Left_Child'] != 'FF' else 'FF'
            right_child = format(int(row['Right_Child'], 16) + offset, '02X') if row['Right_Child'] != 'FF' else 'FF'
            prediction  = row['Prediction'].upper().rjust(2, '0')

            hex_line = feature + threshold + left_child + right_child + prediction
            lines.append(hex_line)
        
        all_lines.extend(lines)
        offset += len(lines)

with open(output_file, 'w') as hexfile:
    for line in all_lines:
        hexfile.write(line + '\n')
