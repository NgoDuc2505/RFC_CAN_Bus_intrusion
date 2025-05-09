import csv

# [9bit Node][2 bit feature][64 bit threshold][9 bit left][9 bit right][2 bit prediction]
# [3hex Node][1 hex feature][16 hex threshold][3 hex left][3 hex right][1 hex prediction]

def convert_to_bin_threshold(threshold):
    # Kiểm tra nếu threshold là một số thực (float)
    try:
        threshold_float = float(threshold)
        if threshold_float == float('inf') or threshold_float == float('-inf'):
            # Nếu là vô cùng
            threshold_bin = '1' + '0' * 63  # Đặt threshold là vô cùng
        else:
            # Chuyển đổi sang chuỗi nhị phân 64 bit
            threshold_bin = format(int(threshold_float), '064b')
    except ValueError:
        # Nếu không phải là số thực, kiểm tra xem có phải hex không
        try:
            # Nếu threshold là hex
            threshold_hex = threshold.strip()  # Xóa khoảng trắng nếu có
            if len(threshold_hex) <= 16:
                threshold_int = int(threshold_hex, 16)  # Chuyển từ hex sang số nguyên
                threshold_bin = format(threshold_int, '064b')
            else:
                # Nếu threshold là một hex dài hơn 16 ký tự, đảm bảo chỉ lấy 64 bit
                threshold_int = int(threshold_hex, 16) & ((1 << 64) - 1)  # Đảm bảo chỉ lấy 64 bit
                threshold_bin = format(threshold_int, '064b')
        except ValueError:
            # Nếu không phải số thực hoặc hex, mặc định là 0
            threshold_bin = '0' * 64  # Nếu không thể chuyển thành float hoặc hex thì mặc định là 0

    return threshold_bin


def convert_to_hex(node, feature, threshold, left_child, right_child, prediction):
    # Chuyển Node (9 bit = 3 hex)
    node_bin = format(node, '09b')

    # Feature (2 bit = 1 hex)
    feature_bin = '11' if feature == '-1' else format(int(feature), '02b')

    # Threshold (64 bit = 16 hex)
    threshold_bin = convert_to_bin_threshold(threshold)

    # Left child (9 bit = 3 hex)
    left_bin = format(left_child, '09b')

    # Right child (9 bit = 3 hex)
    right_bin = format(right_child, '09b')

    # Prediction (2 bit = 1 hex)
    if prediction == '-1':
        prediction_bin = '11'
    elif prediction == '1':
        prediction_bin = '01'
    else:
        prediction_bin = '00'

    # Chuyển tất cả các phần tử nhị phân sang hexadecimal

    return node_bin + feature_bin + threshold_bin + left_bin + right_bin + prediction_bin


# Đọc dữ liệu từ file CSV và chuyển đổi
def convert_csv_to_mif(tree_id, output_mif):
    input_csv = f"LUT/tree_{tree_id}_v.csv"  # Đường dẫn file CSV động

    # Đọc CSV
    with open(input_csv, mode='r') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)  # Bỏ qua tiêu đề

        # Mở file .mif để ghi
        with open(output_mif, mode='w') as miffile:
            # Duyệt qua từng dòng CSV và chuyển đổi
            for row in csvreader:
                node = int(row[0])
                feature = row[1]
                threshold = row[2]
                left_child = int(row[3])
                right_child = int(row[4])
                prediction = row[5]

                # Chuyển chuỗi nhị phân thành HEX
                hex_string = convert_to_hex(node, feature, threshold, left_child, right_child, prediction)

                # Ghi vào file .mif
                miffile.write(f"{hex_string}\n")


# Duyệt qua tất cả các tree_id từ 0 đến 20 và chuyển đổi
for tree_id in range(21):  
    output_mif = f"LUT/tree_{tree_id}_output.mif"  
    convert_csv_to_mif(tree_id, output_mif)
    print(f"Chuyển đổi tree_{tree_id}_v.csv thành {output_mif} hoàn tất!")
