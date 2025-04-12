import os

file_path = "src/LUT/split_model_v4_00.csv"

if os.path.exists(file_path):
    print("✅ Tệp tồn tại.")
else:
    print("❌ Tệp không tồn tại. Kiểm tra lại đường dẫn!")
