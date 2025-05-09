import os
import pandas as pd
import math

def print_max_column_bit_lengths_in_directory(directory_path):
    # Duyệt qua tất cả các tệp CSV trong thư mục
    for filename in os.listdir(directory_path):
        if filename.endswith(".csv") and filename.startswith("tree_"):
            file_path = os.path.join(directory_path, filename)
            print(f"\nĐọc file: {filename}")
            print_max_column_bit_lengths(file_path)

def print_max_column_bit_lengths(csv_path):
    # Đọc dữ liệu từ file CSV
    df = pd.read_csv(csv_path)
    
    # In ra độ dài dữ liệu tối đa theo bit và hex của từng cột
    print("Độ dài dữ liệu tối đa theo bit và hex của từng cột:")
    for column in df.columns:
        max_bit_length = df[column].apply(lambda x: compute_bit_length(x)).max()
        max_hex_length = (max_bit_length + 3) // 4  # Chuyển từ bit sang hex
        print(f"{column}: {max_bit_length} bits, {max_hex_length} hex")

def compute_bit_length(x):
    try:
        # Kiểm tra xem giá trị có phải là vô hạn hoặc NaN không
        if isinstance(x, str):
            # Chuyển đổi hex sang số và tính độ dài bit
            return len(bin(int(x, 16))[2:])
        elif isinstance(x, (int, float)):
            # Kiểm tra giá trị NaN hoặc vô hạn
            if math.isinf(x) or math.isnan(x):
                return 0  # Đặt 0 bit nếu là giá trị vô hạn hoặc NaN
            return len(bin(int(x))[2:])
        else:
            return 0  # Trường hợp không hợp lệ, trả về 0 bit
    except Exception as e:
        print(f"Không thể xử lý giá trị: {x}, lỗi: {e}")
        return 0

if __name__ == "__main__":
    # Đường dẫn đến thư mục chứa các tệp CSV của bạn
    directory_path = 'LUT/'  # Thay đổi đường dẫn nếu cần
    print_max_column_bit_lengths_in_directory(directory_path)
