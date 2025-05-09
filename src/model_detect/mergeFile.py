import os
import pandas as pd

# Đường dẫn đến thư mục chứa các file CSV
folder_path = 'src/model_tree_latest'

# Tạo list để chứa tất cả các DataFrame
dfs = []

# Duyệt qua tất cả các file trong thư mục
for filename in os.listdir(folder_path):
    if filename.endswith('.csv'):
        # Đọc từng file CSV và thêm vào list
        file_path = os.path.join(folder_path, filename)
        df = pd.read_csv(file_path)
        dfs.append(df)

# Gộp tất cả các DataFrame thành một
merged_df = pd.concat(dfs, ignore_index=True)

# Lưu thành file CSV mới
merged_df.to_csv('src/datasets_release/set_03/sample_1.csv', index=False)

print(f"Đã gộp {len(dfs)} file CSV thành can-data-set-03.csv")