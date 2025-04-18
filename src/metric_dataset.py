import pandas as pd
import os
def metric_label(inputCSV, label_name = "attack"):
    try:
        df = pd.read_csv(inputCSV)
    except FileNotFoundError:
        print(f"File: {inputCSV} not found.")
        return None
    label_counts = df[label_name].value_counts()
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

def balance_dataset_label(inputCSV, outputDir, output_file_name = "balanced_dataset.csv"):
    isExist = not os.path.exists(outputDir) and not os.path.isdir(outputDir)
    if isExist:
        os.makedirs(outputDir)
        print(f"📁 Folder created: {outputDir}")
    else:
        print(f"📁 Folder already exists: {outputDir}")
    path = os.path.join(outputDir, output_file_name)
    try:
        df = pd.read_csv(inputCSV)
        # Lọc theo class
        df_0 = df[df["attack"] == 0]
        df_1 = df[df["attack"] == 1]


        total_samples = min(len(df_0), len(df_1)) * 2
        n_0 = int(total_samples * 0.51)
        n_1 = total_samples - n_0  

        df_0_sampled = df_0.sample(n=n_0, random_state=42)
        df_1_sampled = df_1.sample(n=n_1, random_state=42, replace=True)  # Cho phép lặp nếu cần

        df_balanced = pd.concat([df_0_sampled, df_1_sampled]).sample(frac=1, random_state=42)  # Shuffle

        df_balanced.to_csv(path, index=False)

        print(f"Balanced dataset saved with {len(df_balanced)} rows at {path}")
        label_counts, total_sample = metric_label(path)
        if label_counts is not None:
            print(f"dataset: {path}")
            print(f"class {0}: {(float(label_counts.to_dict()[0]) / float(total_sample)).__round__(3)} % : {(label_counts.to_dict()[0])}")
            print(f"class {1}: {(float(label_counts.to_dict()[1]) / float(total_sample)).__round__(3)} % : {(label_counts.to_dict()[1])}")
            print(f"total: {total_sample}")
    except FileNotFoundError:
        print(f"File: {inputCSV} not found.")
        return None

    

if __name__ == "__main__":
    # inputCSV = "src/datasets/train_split_label/full_dataset/merged_train_set_01_with_02_03_04_label_1.csv" 
    # inputCSV2 = "src/datasets/train_01/set_01/merged_train_01/merged_train_set_01.csv" 
    # label_counts, total_sample = metric_label(inputCSV2)
    # if label_counts is not None:
    #     print(f"dataset: {inputCSV2}")
    #     print(f"class {0}: {(float(label_counts.to_dict()[0]) / float(total_sample)).__round__(3)} % : {(label_counts.to_dict()[0])}")
    #     print(f"class {1}: {(float(label_counts.to_dict()[1]) / float(total_sample)).__round__(3)} % : {(label_counts.to_dict()[1])}")
    #     print(f"total: {total_sample}")
    # inputCSV_2 = "test_result_with_prediction.csv" 
    # label_counts_2, total_sample_2 = metric_label(inputCSV_2, label_name="prediction")
    # if label_counts_2 is not None:
    #     print(f"dataset: {inputCSV}")
    #     print(f"class {0}: {(float(label_counts_2.to_dict()[0]) / float(total_sample)).__round__(3)} % : {(label_counts_2.to_dict()[0])}")
    #     print(f"class {1}: {(float(label_counts_2.to_dict()[1]) / float(total_sample)).__round__(3)} % : {(label_counts_2.to_dict()[1])}")
    #     print(f"total: {total_sample}")  

    inputCSV_folder = "src/su2017/extra-attack-free"
    # csv_amount, files, _ = metric_file_csv(inputCSV_folder)

    # amount, _ = deep_metric_file_csv(inputCSV_folder, "src/su2017/extra-attack-free/summary")
    balance_dataset_label("src/datasets/train_split_label/full_dataset/merged_train_set_01_with_02_03_04_label_1.csv", "src/datasets/train_split_label/full_dataset", output_file_name="balanced_dataset.csv")