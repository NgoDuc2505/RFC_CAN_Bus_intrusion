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

def merge_csv_by_list(inputCSV_file_list, save_dir=None, file_name=None):
    df_list = pd.DataFrame()
    title = "total input files"
    try:
        for files in inputCSV_file_list:
            df = pd.read_csv(files)
            df_list = pd.concat([df_list, df], ignore_index=True)
            print(f"File: {files} has {df.shape[0]} samples and {df[df.duplicated()].shape[0]} duplicate samples.")
        print(f"🧳total sample in {title}: {df_list.shape[0]}")
        dup = df_list[df_list.duplicated()]
        print(f"🧨 File: {title} has {dup.shape[0]} duplicate samples.")
        removed_list = df_list.drop_duplicates()
        print(f"🥇 File: {title} has {removed_list.shape[0]} samples after removing duplicates.")
        if save_dir is not None:
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
                print(f"📁 Folder created: {save_dir}")
            if file_name is None:
                path_output = os.path.join(save_dir, "summary.csv")
            path_output = os.path.join(save_dir, file_name)
            removed_list.to_csv(path_output, index=False)
            print(f"File: {path_output} has {removed_list.shape[0]} samples after removing duplicates.")
            removed_list.to_csv(path_output, index=False)
    except FileNotFoundError:
        print(f"File: not found.")
        return None
    
def full_merge_convert(dirList, label_list, save_dir=None, file_name=None):
    files_stack = []
    for i, dir in enumerate(dirList):
        if os.path.isdir(dir) and os.path.exists(dir):
            files = [f for f in os.listdir(dir) if f.endswith(".csv")]
            files_stack = files_stack + files
            # print(f"Directory: {dir} label {label_list[i]}.")
        else:
            print(f"Directory: {dir} not found.")
            continue
    print(f"total files: {len(files_stack)}")
    for file in files_stack:
        print(f"File: {file} label {label_list[i]}.")
            

if __name__ == "__main__":
    inputCSV = "src/datasets_release/can_data_v7_2.csv" 
    label_counts, total_sample = metric_label(inputCSV)
    if label_counts is not None:
        print(f"dataset: {inputCSV}")
        print(f"class {0}: {(float(label_counts.to_dict()[0]) / float(total_sample)).__round__(3)} % : {(label_counts.to_dict()[0])}")
        print(f"class {1}: {(float(label_counts.to_dict()[1]) / float(total_sample)).__round__(3)} % : {(label_counts.to_dict()[1])}")
        print(f"total: {total_sample}")
    
    inputCSV_folder = "src/su2017/extra-attack-free"
    inputCSV_folder_2 = "src/su2017/DoS-attacks"
    inputCSV_folder_3 = "src/su2017/fuzzing-attacks"
    inputCSV_folder_3 = "src/su2017/attack-free"
    inputCSV_folder_4 = "src/su2017"
    csv_amount, files, _ = metric_file_csv(inputCSV_folder_4)
  
