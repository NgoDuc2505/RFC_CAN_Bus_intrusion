import csv

# Danh sách file đầu vào
input_files = [
    'split_model_v4_v2/split_model_v4_v2_00.csv',
    'split_model_v4_v2/split_model_v4_v2_01.csv',
    'split_model_v4_v2/split_model_v4_v2_10.csv'
]

output_file = 'split_model_v4_v2/LUTModel_hex.hex'
offset = 0
all_lines = []

for file in input_files:
    with open(file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        lines = []
        for row in reader:
            tree        = row['Tree'].upper().rjust(2, '0')  # Thêm dòng này để lấy giá trị Tree
            feature     = format(int(row['Feature'], 16), '02X')
            threshold   = format(int(row['Threshold'], 16), '04X')
            left_child  = format(int(row['Left_Child'], 16) + offset, '02X') if row['Left_Child'] != 'FF' else 'FF'
            right_child = format(int(row['Right_Child'], 16) + offset, '02X') if row['Right_Child'] != 'FF' else 'FF'
            prediction  = row['Prediction'].upper().rjust(2, '0')

            hex_line = tree + feature + threshold + left_child + right_child + prediction  # Thêm tree vào hex_line
            lines.append(hex_line)
        
        all_lines.extend(lines)
        offset += len(lines)

with open(output_file, 'w') as hexfile:
    for line in all_lines:
        hexfile.write(line + '\n')