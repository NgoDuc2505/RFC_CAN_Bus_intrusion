import pandas as pd
import os
def metric_label(inputCSV):
    try:
        df = pd.read_csv(inputCSV)
    except FileNotFoundError:
        print(f"File: {inputCSV} not found.")
        return None
    label_counts = df['label'].value_counts()
    total_sample = df.shape[0]
    return label_counts, total_sample

def metric_file_csv(inputCSV_folder):
    try:
        csv_amount = len([f for f in os.listdir(inputCSV_folder) if f.endswith(".csv")])
        files = [f for f in os.listdir(inputCSV_folder) if f.endswith(".csv")]
    except FileNotFoundError:
        print(f"File: {inputCSV_folder} not found.")
        return None
    count_total = 0
    for file in files:
        df = pd.read_csv(os.path.join(inputCSV_folder, file))
        duplicate = df[df.duplicated()]
        count_total += df.shape[0]
        print(f"File: {file} has {duplicate.shape[0]} duplicate samples.")
    print(f"total sample in {inputCSV_folder}: {count_total}")
    return csv_amount, files, count_total

def deep_metric_file_csv(inputCSV_folder, output_file):
    df_list = []
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"📁 Folder created: {output_dir}")

    try:
        files = [f for f in os.listdir(inputCSV_folder) if f.endswith(".csv")]
    except FileNotFoundError:
        print(f"File: {inputCSV_folder} not found.")
        return None
    try:
        for file in files:
            df = pd.read_csv(os.path.join(inputCSV_folder, file))
            df_list.append(df)
    except Exception as e:
        print(f"Error reading files in {inputCSV_folder}: {e}")

    path_output = os.path.join(output_dir, "summary.csv")
    merged_df = pd.concat(df_list, ignore_index=True)
    merged_df.to_csv(path_output, index=False)

    df_s = pd.read_csv(path_output)
    amount = df_s.shape[0]
    duplicate = df_s[df_s.duplicated()]
    print(f"File: {output_file} has {duplicate.shape[0]} duplicate samples.")
    print(f"total sample in {inputCSV_folder}: {amount}")
    return amount, df_s


if __name__ == "__main__":
    inputCSV = "src/datasets_release/can_data_v7_2.csv" 
    label_counts, total_sample = metric_label(inputCSV)
    if label_counts is not None:
        print(f"dataset: {inputCSV}")
        print(f"class {0}: {(float(label_counts.to_dict()[0]) / float(total_sample)).__round__(3)} % : {(label_counts.to_dict()[0])}")
        print(f"class {1}: {(float(label_counts.to_dict()[1]) / float(total_sample)).__round__(3)} % : {(label_counts.to_dict()[1])}")
        print(f"total: {total_sample}")
    
    inputCSV_folder = "src/su2017/extra-attack-free"
    csv_amount, files, _ = metric_file_csv(inputCSV_folder)

    amount, _ = deep_metric_file_csv(inputCSV_folder, "src/su2017/extra-attack-free/summary")
