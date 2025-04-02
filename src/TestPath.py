import os

file_path = "RFC_CAN_Bus_intrusion/src/random_forest_model_v7_2.pkl"

if os.path.exists(file_path):
    print("✅ Tệp tồn tại.")
else:
    print("❌ Tệp không tồn tại. Kiểm tra lại đường dẫn!")
