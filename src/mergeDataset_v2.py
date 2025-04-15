import os
import pandas as pd
from collections import Counter
import numpy as np

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
    df["data_entropy"] = df["data_field"].apply(calculate_entropy).round(5)
    return df

def preprocess_dataframe(df):
    df["arbitration_id"] = df["arbitration_id"].apply(lambda x: int(x, 16))
    df["timestamp"] = df["timestamp"].astype(float)
    df["inter_arrival_time"] = df.groupby("arbitration_id")["timestamp"].diff().fillna(0).round(6)
    return df


def merge_csv_files(input_files, output_file, output_file_name = "dataset_updated_v1.csv", mode="push", label=0):
    df_list = pd.DataFrame()

    if mode == "push":
        df_list = pd.read_csv(os.path.join(output_file, "dataset_updated_v1.csv"))
        samples_count = len(df_list)
        print(f"Data already merged: {samples_count} samples")

    _, output_dir = check_dir(output_file)

    try:
        files = [f for f in os.listdir(input_files) if f.endswith(".csv")]
    except FileNotFoundError:
        print(f"File: {input_files} not found.")
        return None
    try:
        for file in files:
            print(f"Reading file: {file}")
            df = pd.read_csv(os.path.join(input_files, file))
            df = preprocess_dataframe(df)
            df = compute_entropy_for_dataframe(df)
            df['dls'] = df['data_field'].apply(lambda x: len(str(x).replace(" ", "")) // 2)
            df = df.drop(columns=["timestamp"])
            df.drop(columns=['data_field'], inplace=True)
            df["label"] = label
            df_list = pd.concat([df_list, df], ignore_index=True)
    except Exception as e:
        print(f"Error reading files in {input_files}: {e}")

    out_path = os.path.join(output_dir, output_file_name)
    df_list.to_csv(out_path, index=False)
    print(f"All data merged into: {out_path}, including: {len(df_list)} samples")
    return out_path

def check_duplicate(inputCSV):
    try:
        df = pd.read_csv(inputCSV)
        print(f"samples count: {len(df)}")
    except FileNotFoundError:
        print(f"File: {inputCSV} not found.")
        return None
    duplicate = df[df.duplicated()]
    print(f"File: {inputCSV} has {duplicate.shape[0]} duplicate samples.")
    if duplicate.shape[0] > 0:
        df_clean = df.drop_duplicates()
        df_clean.to_csv(inputCSV, index=False)
        print(f"Duplicate samples removed from {inputCSV}, samples count: {len(df_clean)}.")
    return inputCSV

def check_dir(inputDir: str):
    isExist = not os.path.exists(inputDir) and not os.path.isdir(inputDir)
    if isExist:
        os.makedirs(inputDir)
        print(f"📁 Folder created: {inputDir}")
    else:
        print(f"📁 Folder already exists: {inputDir}")
    return isExist, inputDir

if __name__ == "__main__":
    input_files = "/content/drive/MyDrive/Notebook_Colab/RFC/Dataset/extra-attack-free"
    input_files1 = "/content/drive/MyDrive/Notebook_Colab/RFC/dataset_processing/dir_attck_free"
    input_files2 = "/content/drive/MyDrive/Notebook_Colab/RFC/Dataset/DoS-attacks"
    input_files3 = "/content/drive/MyDrive/Notebook_Colab/RFC/Dataset/fuzzing-attacks"
    input_files4 = "/content/drive/MyDrive/Notebook_Colab/RFC/Dataset/gear-attacks"
    input_files5 = "/content/drive/MyDrive/Notebook_Colab/RFC/Dataset/interval-attacks"
    input_files6 = "/content/drive/MyDrive/Notebook_Colab/RFC/Dataset/rpm-attacks"
    input_files7 = "/content/drive/MyDrive/Notebook_Colab/RFC/Dataset/speed-attacks"
    input_files8 = "/content/drive/MyDrive/Notebook_Colab/RFC/Dataset/standstill-attacks"
    input_files9 = "/content/drive/MyDrive/Notebook_Colab/RFC/Dataset/systematic-attacks"
    output_file = "/content/drive/MyDrive/Notebook_Colab/RFC/dataset_processing/v1"
    # output_path = merge_csv_files(input_files1, output_file, mode="normal", label=0)
    # output_path = merge_csv_files(input_files2, output_file, mode="push", label=1)
    # output_path = merge_csv_files(input_files3, output_file, mode="push", label=1)
    output_path =check_duplicate("/content/drive/MyDrive/Notebook_Colab/RFC/dataset_processing/v1/dataset_updated_v1.csv")