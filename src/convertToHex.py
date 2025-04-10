import pandas as pd
import os
import numpy as np

def convertToHexFile(input: str, outDir: str):
    try:
        data = pd.read_csv(input)
        print(data)
    except FileNotFoundError:
        print(f"File {input} không tồn tại.")
        exit(1)
    
    def to_hex(val, bits):
        return format(val & ((1 << bits) - 1), '0' + str(bits // 4) + 'x')

    if not os.path.exists(outDir):
        os.makedirs(outDir)

    hex_lines = []
    for index, row in data.iterrows():
        
        tree = int(row['Tree'])
        node = int(row['Node'])

        feature_map = {'T_A': 0, 'A_ID': 1, 'DLS': 2, 'D_E': 3, np.nan: 255}
        feature = feature_map[row['Feature']]

        if (np.isnan(row['Threshold'])):
            threshold = 0xFFFF  
        else:
            threshold_float = float(row['Threshold'])
            threshold = int(threshold_float * (2**6))  
            if threshold > 0xFFFF:  
                threshold = 0xFFFF

        
        left_child = 255 if (np.isnan(row['Left_Child'])) else int(row['Left_Child'])
        right_child = 255 if (np.isnan(row['Right_Child'])) else int(row['Right_Child'])

    
        prediction = 255 if (np.isnan(row['Prediction'])) else int(row['Prediction'])
        combined = (tree << 56) | (node << 48) | (feature << 40) | (threshold << 24) | (left_child << 16) | (right_child << 8) | prediction
        hex_line = to_hex(combined, 64)  
        hex_lines.append(hex_line)

    pathOutput = os.path.join(outDir, "output.hex")
    with open(pathOutput, 'w') as f:
        for line in hex_lines:
            f.write(line + '\n')

    print(f"Chuyển đổi hoàn tất! File {pathOutput} đã được tạo.")


if __name__ == "__main__":
    convertToHexFile("random_forest_model_v4_optimized_LUT.csv", "hex_lut")