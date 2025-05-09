import os
import pandas as pd

# Đường dẫn tới thư mục chứa các file CSV
folder_path = "LUT/"

# Duyệt qua tất cả các file trong thư mục
for filename in os.listdir(folder_path):
    if filename.endswith(".csv"):
        file_path = os.path.join(folder_path, filename)
        
        # Đọc file CSV
        df = pd.read_csv(file_path)
        
        # Kiểm tra và xóa phần ".0" nếu có ở cột threshold
        if 'threshold' in df.columns:
            df['threshold'] = df['threshold'].apply(lambda x: int(x) if x == int(x) else x)
        
        # Lưu lại file CSV đã chỉnh sửa
        df.to_csv(file_path, index=False)
        print(f"Đã xử lý file: {filename}")
