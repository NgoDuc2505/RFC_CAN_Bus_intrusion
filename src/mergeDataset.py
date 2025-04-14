import os
import pandas as pd

def merge_csv_files(input_files, output_file, output_file_name = "dataset_updated_v1.csv", mode="push"):
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
    except FileNotFoundError:
        print(f"File: {inputCSV} not found.")
        return None
    duplicate = df[df.duplicated()]
    print(f"File: {inputCSV} has {duplicate.shape[0]} duplicate samples.")
    return duplicate.shape[0]

def check_dir(inputDir: str):
    isExist = not os.path.exists(inputDir) and not os.path.isdir(inputDir)
    if isExist:
        os.makedirs(inputDir)
        print(f"📁 Folder created: {inputDir}")
    else:
        print(f"📁 Folder already exists: {inputDir}")
    return isExist, inputDir

if __name__ == "__main__":
    input_files = "src/su2017/extra-attack-free"
    input_files2 = "src/su2017/attack-free"
    output_file = "src/datasets/merge_dataset"
    output_path = merge_csv_files(input_files, output_file, mode="normal")
    output_path = merge_csv_files(input_files2, output_file, mode="push")
    check_duplicate(output_path)