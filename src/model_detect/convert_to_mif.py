import csv

#[9bit Node][2 bit feature][64 bit threshold][9 bit left][9 bit right][2 bit prediction]
#[3hex Node][1 hex feature][16 hex threshold][3 hex left][3 hex right][1 hex prediction]
def convert_to_hex(node, feature, threshold, left_child, right_child, prediction):
    # Chuyển Node (9 bit = 3 hex)
    node_bin = format(node, '09b')
    hex_node = format(int(node_bin, 2), '03X')

    # Feature (2 bit = 1 hex)
    feature_bin = '11' if feature == '-1' else format(int(feature), '02b')
    hex_feature = format(int(feature_bin, 2), '01X')

    # Threshold (64 bit = 16 hex)
    threshold_bin = format(int(threshold, 16), '064b')
    hex_threshold = format(int(threshold_bin, 2), '016X')

    # Left child (9 bit = 3 hex)
    left_bin = format(left_child, '09b')
    hex_left = format(int(left_bin, 2), '03X')

    # Right child (9 bit = 3 hex)
    right_bin = format(right_child, '09b')
    hex_right = format(int(right_bin, 2), '03X')

    # Prediction (2 bit = 1 hex)
    if prediction == '-1':
        prediction_bin = '11'
    elif prediction == '1':
        prediction_bin = '01'
    else:
        prediction_bin = '00'
    hex_prediction = format(int(prediction_bin, 2), '01X')

    # Ghép tất cả lại
    
    return hex_node + hex_feature + hex_threshold + hex_left + hex_right + hex_prediction

# Đọc dữ liệu từ file CSV và chuyển đổi
def convert_csv_to_mif(tree_id, output_mif):
    input_csv = f"LUT/tree_{tree_id}_v.csv"  # Đường dẫn file CSV động

    # Đọc CSV
    with open(input_csv, mode='r') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)  # Bỏ qua tiêu đề

        # Mở file .mif để ghi
        with open(output_mif, mode='w') as miffile:
            miffile.write("WIDTH=96;\n")  # Sửa WIDTH thành 96 để phù hợp với 96 bit
            miffile.write("DEPTH=512;\n")
            miffile.write("ADDRESS_RADIX=UNS;\n")
            miffile.write("DATA_RADIX=BIN;\n")  # Sử dụng dữ liệu nhị phân trong MIF
            miffile.write("CONTENT BEGIN\n")

            # Duyệt qua từng dòng CSV và chuyển đổi
            for row in csvreader:
                node = int(row[0])
                feature = row[1]
                threshold = row[2]
                left_child = int(row[3])
                right_child = int(row[4])
                prediction = row[5]

                # Chuyển đổi dòng CSV thành chuỗi nhị phân
                # binary_string = convert_to_binary(node, feature, threshold, left_child, right_child, prediction)

                # Chuyển chuỗi nhị phân thành HEX
                hex_string = convert_to_hex(node, feature, threshold, left_child, right_child, prediction)

                # Ghi vào file .mif
                miffile.write(f"    {node} : {hex_string};\n")

            miffile.write("END;\n")

# Duyệt qua tất cả các tree_id từ 0 đến 20 và chuyển đổi
for tree_id in range(21):  # tree_id từ 0 đến 20
    output_mif = f"LUT/tree_{tree_id}_output.mif"  # Đặt tên file .mif xuất ra
    convert_csv_to_mif(tree_id, output_mif)
    print(f"Chuyển đổi tree_{tree_id}_v.csv thành {output_mif} hoàn tất!")
