import csv

# Hàm chuyển đổi một dòng CSV sang chuỗi nhị phân
def convert_to_binary(node, feature, threshold, left_child, right_child, prediction):
    # Chuyển Node (10 bit)
    node_bin = format(node, '010b')

    # Chuyển Feature (4 bit), nếu feature là -1 thì dùng '1111'
    feature_bin = '1111' if feature == '-1' else format(int(feature), '04b')

    # Threshold (64 bit HEX)
    threshold_bin = format(int(threshold, 16), '064b')

    # Left Child (10 bit)
    left_child_bin = format(left_child, '010b')

    # Right Child (10 bit)
    right_child_bin = format(right_child, '010b')

    # Prediction (2 bit), nếu prediction là -1 thì dùng '11', nếu prediction là 1 thì dùng '01', còn lại là '00'
    if prediction == '-1':
        prediction_bin = '11'
    elif prediction == '1':
        prediction_bin = '01'
    else:
        prediction_bin = '00'

    # Kết hợp tất cả các phần lại với nhau
    return node_bin + feature_bin + threshold_bin + left_child_bin + right_child_bin + prediction_bin

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
                binary_string = convert_to_binary(node, feature, threshold, left_child, right_child, prediction)

                # Chuyển chuỗi nhị phân thành HEX
                hex_string = hex(int(binary_string, 2))[2:].upper()

                # Ghi vào file .mif
                miffile.write(f"    {node} : {hex_string};\n")

            miffile.write("END;\n")

# Duyệt qua tất cả các tree_id từ 0 đến 20 và chuyển đổi
for tree_id in range(21):  # tree_id từ 0 đến 20
    output_mif = f"LUT/tree_{tree_id}_output.mif"  # Đặt tên file .mif xuất ra
    convert_csv_to_mif(tree_id, output_mif)
    print(f"Chuyển đổi tree_{tree_id}_v.csv thành {output_mif} hoàn tất!")
