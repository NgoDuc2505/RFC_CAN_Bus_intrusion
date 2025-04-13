import pandas as pd
import numpy as np
import struct
import os

# Ánh xạ feature names sang giá trị số
feature_mapping = {'00': 0, '01': 1, '10': 10, '11': 11}

def convert_tree_to_bin(csv_path, bin_path):
    df = pd.read_csv(csv_path)
    
    with open(bin_path, 'wb') as bin_file:
        for _, row in df.iterrows():
            # Xác định node type (leaf/internal)
            is_leaf = 1 if pd.isna(row['Feature']) or str(row['Feature']).strip() == '' else 0
            
            # Xử lý Feature
            if is_leaf:
                feature = 0  # 00000000 cho leaf node
            else:
                feature = feature_mapping.get(str(row['Feature']).strip(), 0)
            
            # Xử lý Left và Right Child
            left_child = int(float(row['Left_Child'])) if not pd.isna(row['Left_Child']) else 0
            right_child = int(float(row['Right_Child'])) if not pd.isna(row['Right_Child']) else 0
            
            # Xử lý Threshold
            threshold = float(row['Threshold']) if not pd.isna(row['Threshold']) else 0.0
            
            # Xử lý Prediction
            prediction_str = str(row['Prediction']).strip()
            if prediction_str == 'FF':
                prediction = 0xFF  # 11111111 cho non-leaf node
                is_leaf = 0  # Đảm bảo FF là non-leaf
            elif pd.isna(row['Prediction']) or prediction_str == '':
                prediction = 0  # 00000000 mặc định
            else:
                prediction = int(float(prediction_str))
            
            # Pack dữ liệu vào struct (16 bytes)
            node_data = struct.pack(
                '<BHHfBB',  # Little-endian: feature(1), left(2), right(2), threshold(4), prediction(1), is_leaf(1)
                feature,
                left_child,
                right_child,
                threshold,
                prediction,
                is_leaf
            )
            
            # Thêm padding để đảm bảo 16 bytes
            node_data += bytes(5)
            
            bin_file.write(node_data)

def convert_all_trees(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    
    for csv_file in os.listdir(input_dir):
        if csv_file.endswith('.csv'):
            csv_path = os.path.join(input_dir, csv_file)
            bin_path = os.path.join(output_dir, csv_file.replace('.csv', '.bin'))
            convert_tree_to_bin(csv_path, bin_path)
            print(f"Converted {csv_path} to {bin_path}")

# Sử dụng
input_dir = 'src/LUT/'
output_dir = 'src/LUT_bin/'
convert_all_trees(input_dir, output_dir)