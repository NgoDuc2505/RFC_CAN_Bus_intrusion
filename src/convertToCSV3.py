import pandas as pd
import numpy as np
from collections import Counter
import glob

path1 = "su2017"
path2 = "2011-chevrolet-impala"
path3 = "2011-chevrolet-traverse"
path4 = "2016-chevrolet-silverado"

def calculate_entropy(hex_data):
    if(type(hex_data) == float):
        return 0
    if not hex_data or len(hex_data) % 2 != 0:
        return 0 
    
    byte_values = [hex_data[i:i+2] for i in range(0, len(hex_data), 2)]
    
    byte_counts = Counter(byte_values)
    total_bytes = len(byte_values)
    
    probabilities = [count / total_bytes for count in byte_counts.values()]
    entropy = -sum(p * np.log2(p) for p in probabilities if p > 0)
    
    return entropy

def compute_entropy_for_dataframe(df):
    df["data_entropy"] = df["data_field"].apply(calculate_entropy).round(3)
    return df

def preprocess_dataframe(df):
    df["arbitration_id"] = df["arbitration_id"].apply(lambda x: int(x, 16))  
    df["timestamp"] = df["timestamp"].astype(float)  
    df["inter_arrival_time"] = df.groupby("arbitration_id")["timestamp"].diff().fillna(0).round(4)
    return df


def process_and_merge_csv(input_files, output_file, label=0):
    merged_df = pd.DataFrame()
    samples_count = 0
    for file in input_files:
        df = pd.read_csv(file)
        print(f"File {file} có {len(df)} mẫu")
        samples_count += len(df)
        df = preprocess_dataframe(df)
        df = compute_entropy_for_dataframe(df)
        df['dls'] = df['data_field'].apply(lambda x: len(str(x).replace(" ", "")) // 2)
        df = df.drop(columns=["timestamp"])
        df.drop(columns=['data_field'], inplace=True)
        df['label'] = label
        merged_df = pd.concat([merged_df, df], ignore_index=True)

    merged_df.to_csv(output_file, index=False)
    if(samples_count == 0):
        print("Không có dữ liệu nào được gộp")
    else:
        print(f"Tất cả dữ liệu đã được gộp vào: {output_file}, bao gồm: {samples_count} mẫu")    

def process_and_merge_csv_with_mode(input_files, output_file, mode="single", label=0):
    print(f"Xử lý files: {input_files}")
    merged_df = pd.DataFrame()
    samples_count = 0
    if(mode == "single"):
        merged_df = pd.read_csv(output_file)  
        samples_count = len(merged_df)
        print(f"Dữ liệu đã được gộp từ trước: {samples_count} mẫu")  
    for file in input_files:
        df = pd.read_csv(file)
        print(f"File {file} có {len(df)} mẫu")
        samples_count += len(df)
        df = preprocess_dataframe(df)
        df = compute_entropy_for_dataframe(df)
        df['dls'] = df['data_field'].apply(lambda x: len(str(x).replace(" ", "")) // 2)
        df = df.drop(columns=["timestamp"])
        df.drop(columns=['data_field'], inplace=True)
        df['label'] = label
        merged_df = pd.concat([merged_df, df], ignore_index=True)

    merged_df.to_csv(output_file, index=False)
    if(samples_count == 0):
        print("Không có dữ liệu nào được gộp")
    else:
        print(f"Tất cả dữ liệu đã được gộp vào: {output_file}, bao gồm: {samples_count} mẫu")    

crtPath = path1

fs = {
    "free_atk_path": f"src/{crtPath}/attack-free/*.csv",
    "dos_atk_path": f"src/{crtPath}/DoS-attacks/*.csv",
    "fuzzy_atk_path": f"src/{crtPath}/fuzzing-attacks/*.csv",
    "gear_atk_path": f"src/{crtPath}/gear-attacks/*.csv",
    "speed_atk_path": f"src/{crtPath}/speed-attacks/*.csv",
    "interval_atk_path": f"src/{crtPath}/interval-attacks/*.csv",
    "combined_atk_path": f"src/{crtPath}/combined-attacks/*.csv",
    "rpm_atk_path": f"src/{crtPath}/rpm-attacks/*.csv",
    "standstill_atk_path": f"src/{crtPath}/standstill-attacks/*.csv",
    "synsematic_atk_path": f"src/{crtPath}/systematic-attacks/*.csv",
    "output": "src/datasets_release/can_data_v7_3.csv"
}

input_files_atk_free = fs["free_atk_path"]  
input_files_dos = fs["dos_atk_path"]  
input_files_fuz = fs["fuzzy_atk_path"]  
input_files_gear = fs["gear_atk_path"]
input_files_speed = fs["speed_atk_path"] 
input_files_interval = fs["interval_atk_path"]
input_files_combined = fs["combined_atk_path"]
input_files_rpm = fs["rpm_atk_path"]
input_files_standstill = fs["standstill_atk_path"]
input_files_synsematic = fs["synsematic_atk_path"]  
output_file = fs["output"]



process_and_merge_csv(input_files_atk_free, output_file, 0)
process_and_merge_csv_with_mode(input_files_dos, output_file, mode='single', label=1)
process_and_merge_csv_with_mode(input_files_fuz, output_file, mode='single', label=1)
process_and_merge_csv_with_mode(input_files_gear, output_file, mode='single', label=1)
process_and_merge_csv_with_mode(input_files_speed, output_file, mode='single', label=1)
process_and_merge_csv_with_mode(input_files_interval, output_file, mode='single', label=1)
process_and_merge_csv_with_mode(input_files_combined, output_file, mode='single', label=1)
process_and_merge_csv_with_mode(input_files_rpm, output_file, mode='single', label=1)
process_and_merge_csv_with_mode(input_files_standstill, output_file, mode='single', label=1)
process_and_merge_csv_with_mode(input_files_synsematic, output_file, mode='single', label=1)

crtPath = path2

fs = {
    "free_atk_path": f"src/{crtPath}/attack-free/*.csv",
    "dos_atk_path": f"src/{crtPath}/DoS-attacks/*.csv",
    "fuzzy_atk_path": f"src/{crtPath}/fuzzing-attacks/*.csv",
    "gear_atk_path": f"src/{crtPath}/gear-attacks/*.csv",
    "speed_atk_path": f"src/{crtPath}/speed-attacks/*.csv",
    "interval_atk_path": f"src/{crtPath}/interval-attacks/*.csv",
    "combined_atk_path": f"src/{crtPath}/combined-attacks/*.csv",
    "rpm_atk_path": f"src/{crtPath}/rpm-attacks/*.csv",
    "standstill_atk_path": f"src/{crtPath}/standstill-attacks/*.csv",
    "synsematic_atk_path": f"src/{crtPath}/systematic-attacks/*.csv",
    "output": "src/datasets_release/can_data_v7_3.csv"
}

input_files_atk_free = fs["free_atk_path"]  
input_files_dos = fs["dos_atk_path"]  
input_files_fuz = fs["fuzzy_atk_path"]  
input_files_gear = fs["gear_atk_path"]
input_files_speed = fs["speed_atk_path"] 
input_files_interval = fs["interval_atk_path"]
input_files_combined = fs["combined_atk_path"]
input_files_rpm = fs["rpm_atk_path"]
input_files_standstill = fs["standstill_atk_path"]
input_files_synsematic = fs["synsematic_atk_path"]  
output_file = fs["output"]



process_and_merge_csv(input_files_atk_free, output_file, 0)
process_and_merge_csv_with_mode(input_files_dos, output_file, mode='single', label=1)
process_and_merge_csv_with_mode(input_files_fuz, output_file, mode='single', label=1)
process_and_merge_csv_with_mode(input_files_gear, output_file, mode='single', label=1)
process_and_merge_csv_with_mode(input_files_speed, output_file, mode='single', label=1)
process_and_merge_csv_with_mode(input_files_interval, output_file, mode='single', label=1)
process_and_merge_csv_with_mode(input_files_combined, output_file, mode='single', label=1)
process_and_merge_csv_with_mode(input_files_rpm, output_file, mode='single', label=1)
process_and_merge_csv_with_mode(input_files_standstill, output_file, mode='single', label=1)
process_and_merge_csv_with_mode(input_files_synsematic, output_file, mode='single', label=1)
