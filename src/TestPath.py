# Đọc 10 dòng đầu tiên từ tệp .bin
def read_bin_file(file_path, num_lines=10):
    try:
        with open(file_path, 'rb') as file:
            # Đọc 10 dòng (hoặc số lượng dòng bạn muốn) từ tệp nhị phân
            for _ in range(num_lines):
                line = file.read(1)  # Giả sử mỗi dòng có 1 byte
                if line:
                    print(f"Dòng: {line.hex()}")  # In ra giá trị của dòng dưới dạng hex
                else:
                    break
    except FileNotFoundError:
        print(f"Tệp {file_path} không tồn tại.")
    except Exception as e:
        print(f"Lỗi: {e}")

# Đọc 10 dòng đầu tiên từ tệp .bin
read_bin_file('src/LUT/root_bin_00.bin', 10)
