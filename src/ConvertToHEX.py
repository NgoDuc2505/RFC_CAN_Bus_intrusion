import csv
import pandas as pd
import os
from mergeDataset import check_dir


def encode_byte(val):
    return "FF" if val == -1 else f"{int(val):02X}"

def encode_threshold(val):
    # lay hai bytes thap 
    return f"{int(val) & 0xFFFF:04X}" 

def convert_to_hex():
    input_files = [
    'src/LUT/split_model_v4_00.csv',
    'src/LUT/split_model_v4_01.csv',
    'src/LUT/split_model_v4_10.csv'
    ]

    output_file = 'src/LUT/LUTModel_hex.hex'
    offset = 0
    all_lines = []

    for file in input_files:
        with open(file, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            lines = []
            for row in reader:
                tree        = encode_byte(row['Tree'])
                feature     = encode_byte(row['Feature'])
                threshold   = encode_threshold(row['Threshold'])
                left_child  = encode_byte(row['Left_Child'])
                right_child = encode_byte(row['Right_Child'])
                prediction  = encode_byte(row['Prediction'])

                hex_line = tree + feature + threshold + left_child + right_child + prediction  # Thêm tree vào hex_line
                lines.append(hex_line)
            
            all_lines.extend(lines)
            offset += len(lines)

    with open(output_file, 'w') as hexfile:
        for line in all_lines:
            hexfile.write(line + '\n')

def convert_to_hex_from_csv_dir(dirLUT: str, outputDir: str):
    file_dir = os.listdir(dirLUT)
    files_csv = [file for file in file_dir if file.endswith('.csv')]
    output_name = ""
    check_dir(outputDir)
    with open(os.path.join(outputDir, "logger_hex.txt"), 'w', encoding='utf-8') as f:
        f.write(f"Số bytes trên một dòng: 7 bytes \n")
        for i, file in enumerate(files_csv):
            output_name = f"tree_{i}.hex"
            file_path = os.path.join(dirLUT, file)
            pd_file = pd.read_csv(file_path)
            lines = []
            for index, row in pd_file.iterrows():
                tree        = encode_byte(row['Tree'])
                feature     = encode_byte(row['Feature'])
                threshold   = encode_threshold(row['Threshold'])
                left_child  = encode_byte(row['Left_Child'])
                right_child = encode_byte(row['Right_Child'])
                prediction  = encode_byte(row['Prediction'])
                hex_line = tree + feature + threshold + left_child + right_child + prediction
                lines.append(hex_line)
            df_lines = pd.DataFrame(lines)    
            output_path = os.path.join(outputDir, output_name)
            df_lines.to_csv(output_path, index=False, header=False)
            print(f"✅ Đã lưu file {output_name} vào {output_path} bao gồm {len(lines)} node.")
            f.write(f"File: {output_path} bao gồm {len(lines)} node.\n")

def convert_to_hex_from_csv_dir_total(dirLUT: str, outputDir: str):
    file_dir = os.listdir(dirLUT)
    files_csv = [file for file in file_dir if file.endswith('.csv')]
    output_name = "hex_total.hex"
    check_dir(outputDir)
    lines = []
    for file in files_csv:
        file_path = os.path.join(dirLUT, file)
        pd_file = pd.read_csv(file_path)
        for index, row in pd_file.iterrows():
            tree        = encode_byte(row['Tree'])
            feature     = encode_byte(row['Feature'])
            threshold   = encode_threshold(row['Threshold'])
            left_child  = encode_byte(row['Left_Child'])
            right_child = encode_byte(row['Right_Child'])
            prediction  = encode_byte(row['Prediction'])
            hex_line = tree + feature + threshold + left_child + right_child + prediction
            lines.append(hex_line)
    df_lines = pd.DataFrame(lines)
    output_path = os.path.join(outputDir, output_name)
    df_lines.to_csv(output_path, index=False, header=False)
    print(f"✅ Đã lưu file {output_name} vào {output_path} bao gồm {len(lines)} dòng.")

if __name__ == "__main__":
    # convert_to_hex()
    dirLUT = "src/LUT2/"
    outputDir = "src/LUT2/hex/"
    os.makedirs(outputDir, exist_ok=True)
    convert_to_hex_from_csv_dir(dirLUT, outputDir)
    convert_to_hex_from_csv_dir_total(dirLUT, outputDir)