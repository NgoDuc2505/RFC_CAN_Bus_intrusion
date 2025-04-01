import pandas as pd
import os

def modelSplit(csv_file: str, output_dir: str):
    df = pd.read_csv(csv_file)
    
    root_features = df[df["Node"] == "00"][["Tree", "Feature"]]

    groups = root_features.groupby("Feature")
    print(f"{len(groups)} nhóm cây được tìm thấy")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    tree_list_summary = []
    
    for feature, group in groups:
        tree_ids = group["Tree"].tolist()
        tree_list_summary.append(f"Feature={feature}: {len(tree_ids)} cây")
        sub_df = df[df["Tree"].isin(tree_ids)]
        
        output_file = f"{output_dir}_{feature}.csv"
        output_path = os.path.join(output_dir, output_file)

        sub_df.to_csv(output_path, index=False)
        print(f"Đã lưu nhóm cây với root Feature={feature} vào {output_file}")

        summary_file = os.path.join(output_dir, "group_summary.txt")
        with open(summary_file, 'w') as f:
            f.write("Summary of tree groups by root node Feature:\n")
            for line in tree_list_summary:
                f.write(line + "\n")
        
        print(f"Đã lưu thông tin nhóm cây vào {summary_file}")

if __name__ == "__main__":
    csv_file = "random_forest_model_v4_optimized_LUT_mem.csv"  
    output_file_name = "split_model_v4"
    modelSplit(csv_file, output_file_name)