import csv

# Danh sách file đầu vào
input_files = [
    'src/LUT/split_model_v4_00.csv',
    'src/LUT/split_model_v4_01.csv',
    'src/LUT/split_model_v4_10.csv'
]

output_file = 'src/LUT/merged_model.hex'
offset = 0
all_lines = []

for file in input_files:
    with open(file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        lines = []
        for row in reader:
            feature     = format(int(row['Feature'], 16), '02X')
            threshold   = format(int(row['Threshold'], 16), '08X')
            left_child  = format(int(row['Left_Child'], 16) + offset, '02X') if row['Left_Child'] != 'FF' else 'FF'
            right_child = format(int(row['Right_Child'], 16) + offset, '02X') if row['Right_Child'] != 'FF' else 'FF'
            prediction  = row['Prediction'].upper().rjust(2, '0')

            hex_line = feature + threshold + left_child + right_child + prediction
            lines.append(hex_line)
        
        all_lines.extend(lines)
        offset += len(lines)

with open(output_file, 'w') as hexfile:
    for line in all_lines:
        hexfile.write(line + '\n')
