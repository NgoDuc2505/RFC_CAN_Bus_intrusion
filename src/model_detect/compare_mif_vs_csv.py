import csv

def convert_mif_to_csv(input_mif, output_csv):
    with open(input_mif, mode='r') as miffile:
        miflines = miffile.readlines()

    # Mở file CSV để ghi
    with open(output_csv, mode='w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["Node", "Feature", "Threshold_Hex64", "Left_Child", "Right_Child", "Prediction"])

        for line in miflines:
            # Bỏ qua dòng không chứa dữ liệu thực (chẳng hạn dòng header, phần cuối)
            if ':' not in line:
                continue

            # Phân tách dòng theo định dạng của MIF (node : hex_value;)
            parts = line.split(':')
            node = int(parts[0].strip())  # Node là số
            hex_value = parts[1].strip().replace(';', '')  # Dữ liệu hex, loại bỏ dấu ;

            # Chuyển đổi từ HEX thành các phần (Node, Feature, Threshold, Left, Right, Prediction)
            node_bin = format(int(hex_value[:3], 16), '09b')  # Node (3 hex = 9 bit)
            feature_bin = format(int(hex_value[3:4], 16), '04b')  # Feature (1 hex = 4 bit)
            threshold_bin = format(int(hex_value[4:20], 16), '064b')  # Threshold (16 hex = 64 bit)
            left_bin = format(int(hex_value[20:23], 16), '09b')  # Left Child (3 hex = 9 bit)
            right_bin = format(int(hex_value[23:26], 16), '09b')  # Right Child (3 hex = 9 bit)
            prediction_bin = format(int(hex_value[26:27], 16), '02b')  # Prediction (1 hex = 2 bit)

            # Chuyển các phần nhị phân trở lại giá trị ban đầu
            feature = int(feature_bin, 2)
            threshold_value = int(threshold_bin, 2)  # Chuyển threshold sang dạng số nguyên

            # Nếu threshold = 0 thì chuyển thành 0x0000000000000000
            if threshold_value == 0:
                threshold = '0X0000000000000000'
            else:
                threshold = hex(threshold_value).upper()  # Convert threshold về hex

            left_child = int(left_bin, 2)
            right_child = int(right_bin, 2)

            # Chuyển prediction thành giá trị theo định dạng ban đầu
            if prediction_bin == '11':
                prediction = '-1'
            elif prediction_bin == '01':
                prediction = '1'
            else:
                prediction = '0'

            # Viết dòng vào file CSV
            csvwriter.writerow([node, feature, threshold, left_child, right_child, prediction])

    print(f"Chuyển đổi {input_mif} thành {output_csv} hoàn tất!")

# Sử dụng hàm convert_mif_to_csv cho tất cả các tree_id
for tree_id in range(21):  # tree_id từ 0 đến 20
    input_mif = f"LUT/tree_{tree_id}_output.mif"  # Đường dẫn file .mif
    output_csv = f"LUT/tree_{tree_id}_converted.csv"  # Đặt tên file CSV xuất ra
    convert_mif_to_csv(input_mif, output_csv)
    print(f"Chuyển đổi tree_{tree_id}_output.mif thành {output_csv} hoàn tất!")
