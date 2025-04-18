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

def merge_csv_only(input_files, output_file, output_file_name = "dataset_updated_v1.csv"):
    df_list = pd.DataFrame()

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

def check_duplicate_csv_list(inputCSVList):
    df_list = pd.DataFrame()
    try:
        for csv in inputCSVList:
            df = pd.read_csv(csv)
            print(f"samples count: {len(df)}")
            df_list = pd.concat([df_list, df], ignore_index=True)
        print(f"samples count after merge list: {len(df_list)}")
    except FileNotFoundError:
        print(f"File: not found.")
        return None
    duplicate = df_list[df_list.duplicated()]
    print(f"File: list csv has {duplicate.shape[0]} duplicate samples.")
    if duplicate.shape[0] > 0:
        df_clean = df_list.drop_duplicates()
        print(f"Duplicate samples removed from merge list, samples count: {len(df_clean)}.")
    return df_clean

def check_dir(inputDir: str):
    isExist = not os.path.exists(inputDir) and not os.path.isdir(inputDir)
    if isExist:
        os.makedirs(inputDir)
        print(f"📁 Folder created: {inputDir}")
    else:
        print(f"📁 Folder already exists: {inputDir}")
    return isExist, inputDir

def split_dataset_by_label(inputCSVList, outputDir, label = 1, output_file_name = "attack_only_full_set.csv"):
    _, outputDir = check_dir(outputDir)
    save_path = os.path.join(outputDir, output_file_name)
    df_list = pd.DataFrame()
    try:
        for csv in inputCSVList:
            df = pd.read_csv(csv)
            print(f"samples count: {len(df)}")
            df_attack_only = df[df['attack'] == label]
            df_list = pd.concat([df_list, df_attack_only], ignore_index=True)
        df_list.to_csv(save_path, index=False)
        print(f"Data with label {label}, total samples: {len(df_list)} saved to: {save_path}")
        check_duplicate(save_path)
    
    except FileNotFoundError as e:
        print(f"File: not found: {e}.")
        return None

if __name__ == "__main__":
    # input_files = "/content/drive/MyDrive/Notebook_Colab/RFC/Dataset/extra-attack-free"
    # input_files1 = "/content/drive/MyDrive/Notebook_Colab/RFC/dataset_processing/dir_attck_free"
    # input_files2 = "/content/drive/MyDrive/Notebook_Colab/RFC/Dataset/DoS-attacks"
    # input_files3 = "/content/drive/MyDrive/Notebook_Colab/RFC/Dataset/fuzzing-attacks"
    # input_files4 = "/content/drive/MyDrive/Notebook_Colab/RFC/Dataset/gear-attacks"
    # input_files5 = "/content/drive/MyDrive/Notebook_Colab/RFC/Dataset/interval-attacks"
    # input_files6 = "/content/drive/MyDrive/Notebook_Colab/RFC/Dataset/rpm-attacks"
    # input_files7 = "/content/drive/MyDrive/Notebook_Colab/RFC/Dataset/speed-attacks"
    # input_files8 = "/content/drive/MyDrive/Notebook_Colab/RFC/Dataset/standstill-attacks"
    # input_files9 = "/content/drive/MyDrive/Notebook_Colab/RFC/Dataset/systematic-attacks"
    # output_file = "/content/drive/MyDrive/Notebook_Colab/RFC/dataset_processing/v1"
    # output_path = merge_csv_files(input_files1, output_file, mode="normal", label=0)
    # output_path = merge_csv_files(input_files2, output_file, mode="push", label=1)
    # output_path = merge_csv_files(input_files3, output_file, mode="push", label=1)
    # output_path =check_duplicate("/content/drive/MyDrive/Notebook_Colab/RFC/dataset_processing/v1/dataset_updated_v1.csv")
    # input_file = "src/datasets/train_01/set_01/train_01"
    # output_file = "src/datasets/train_01/set_01/merged_train_01"
    # input_file2 = "src/datasets/train_01/set_02/train_01"
    # output_file2 = "src/datasets/train_01/set_02/merged_train_01"
    # input_file3 = "src/datasets/train_01/set_03/train_01"
    # output_file3 = "src/datasets/train_01/set_03/merged_train_01"
    # input_file4 = "src/datasets/train_01/set_04/train_01"
    # output_file4 = "src/datasets/train_01/set_04/merged_train_01"
    # merge_csv_only(input_file, output_file, output_file_name="merged_train_set_01.csv")
    # merge_csv_only(input_file2, output_file2, output_file_name="merged_train_set_02.csv")
    # merge_csv_only(input_file3, output_file3, output_file_name="merged_train_set_03.csv")
    # merge_csv_only(input_file4, output_file4, output_file_name="merged_train_set_04.csv")
    list_csv_check = ["src/datasets/train_01/set_03/merged_train_01/merged_train_set_03.csv",
                   "src/datasets/train_01/set_03/test_01_known_vehicle_known_attack/DoS-2.csv"]
    # check_duplicate_csv_list(list_csv_check)
    # list_split=["src/datasets/train_01/set_02/merged_train_01/merged_train_set_02.csv",
    #             "src/datasets/train_01/set_03/merged_train_01/merged_train_set_03.csv",
    #             "src/datasets/train_01/set_04/merged_train_01/merged_train_set_04.csv"]
    # split_dataset_by_label(list_split, "src/datasets/train_split_label", label=1, output_file_name="attack_only_full_set.csv")
    # merge_csv_only("src/datasets/train_split_label", "src/datasets/train_split_label/full_dataset", output_file_name="merged_train_set_01_with_02_03_04_label_1.csv")
    inputCSVList = [
        "src/datasets/train_01/set_01/test_01_known_vehicle_known_attack/DoS-4.csv",
        "src/datasets/train_01/set_01/test_01_known_vehicle_known_attack/rpm-4.csv"
    ]

    split_dataset_by_label(inputCSVList, "src/datasets/test_split_label", label=1, output_file_name="attack_only_set01_test01_Dos4_rpm4.csv")