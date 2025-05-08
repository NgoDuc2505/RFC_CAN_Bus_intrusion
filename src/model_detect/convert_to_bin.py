# convert_csv_to_bin.py
import pandas as pd
import pickle
import os

for i in range(21):
    csv_path = f"src/LUT2/tree_{i}.csv"
    bin_path = f"src/LUT2/tree_{i}.bin"
    df = pd.read_csv(csv_path)
    with open(bin_path, 'wb') as f:
        pickle.dump(df, f)
    print(f"✅ Đã lưu: {bin_path}")
