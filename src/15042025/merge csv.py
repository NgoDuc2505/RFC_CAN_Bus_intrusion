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

    def balance_dataset(self, df):
        """Cân bằng dataset để giảm overfitting"""
        try:
            class_0 = df[df['label'] == 0]
            class_1 = df[df['label'] == 1]
            if len(class_0) > len(class_1):
                class_0 = class_0.sample(len(class_1), random_state=42)
            else:
                class_1 = class_1.sample(len(class_0), random_state=42)
            return pd.concat([class_0, class_1], ignore_index=True)
        except Exception as e:
            print(f"[!] Lỗi khi cân bằng dataset: {str(e)}")
            return df

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
        result_df = self.balance_dataset(result_df)  # Balance the dataset

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
            "path": "src/15042025/dataset/2017-subaru/attack-free/*.csv",
            "label": 0  # Label 0 cho dữ liệu bình thường
        },
        "attack_paths": {
            "dos": {
                "path": "src/15042025/dataset/2017-subaru/DoS-attacks/*.csv",
                "label": 1
            },
            "fuzzy": {
                "path": "src/15042025/dataset/2017-subaru/fuzzing-attacks/*.csv",
                "label": 1
            },
            "rpm": {
                "path": "src/15042025/dataset/2017-subaru/rpmear-attacks/*.csv",
                "label": 1
            },
            "speed": {
                "path": "src/15042025/dataset/2017-subaru/speed-attacks/*.csv",
                "label": 1
            },
            "systematic": {
                "path": "src/15042025/dataset/2017-subaru/systematic-attacks/*.csv",
                "label": 1
            },
        },
        "output_file": "src/15042025/dataset/2017-subaru/can_data_processed.csv"
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