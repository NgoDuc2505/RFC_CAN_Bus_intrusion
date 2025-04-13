import pandas as pd

def metric_label(inputCSV):
    try:
        df = pd.read_csv(inputCSV)
    except FileNotFoundError:
        print(f"File: {inputCSV} not found.")
        return None
    label_counts = df['label'].value_counts()
    total_sample = df.shape[0]
    return label_counts, total_sample

if __name__ == "__main__":
    inputCSV = "src/datasets_release/can_data_v7_2.csv" 
    label_counts, total_sample = metric_label(inputCSV)
    if label_counts is not None:
        print(f"dataset: {inputCSV}")
        print(f"class {0}: {(float(label_counts.to_dict()[0]) / float(total_sample)).__round__(3)} %")
        print(f"class {1}: {(float(label_counts.to_dict()[1]) / float(total_sample)).__round__(3)} %")
        print(f"total: {total_sample}")