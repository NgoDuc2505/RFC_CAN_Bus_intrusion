import pandas as pd
import binascii
import re
import math
from collections import Counter

def calculate_entropy(data):
    counter = Counter(data)
    total = len(data)
    entropy = -sum((count/total) * math.log2(count/total) for count in counter.values())
    return entropy

def convert_hex_to_dec(string):
    try:
        return int(string, 16)
    except ValueError:
        return int(binascii.hexlify(string.encode('utf-8')), 16)
    except TypeError:
        return int(hex(0,), 16)

def hex_to_decimal(hex_string):
    return int(hex_string, 16)

def parse_can_log(txt_file, csv_file):
    data_list = []
    prev_timestamp = None
    
    with open(txt_file, 'r') as file:
        for line in file:
            match = re.search(r'Timestamp:\s+(\d+\.\d+)\s+ID:\s+([0-9A-Fa-f]+)\s+\d+\s+DLC:\s+(\d+)\s+([0-9A-Fa-f\s]+)', line)
            
            if match:
                timestamp = float(match.group(1))
                arbitration_id = hex_to_decimal(match.group(2))
                dlc = int(match.group(3))
                data_hex = match.group(4).split()
                
                # Chuyển đổi data từ hex sang thập phân
                # data_decimals = [convert_hex_to_dec(byte) for byte in data_hex]
                # data_string = ' '.join(map(str, data_decimals))

                data_decimals_entropy = calculate_entropy(data_hex)
                data_string = "" + str(data_decimals_entropy)
                
                # Tính Inter-Arrival Time
                inter_arrival_time = (timestamp - prev_timestamp) if prev_timestamp is not None else 0
                prev_timestamp = timestamp
                
                data_list.append([inter_arrival_time, arbitration_id, dlc, data_string, 0])
    
    # Lưu vào file CSV
    df = pd.DataFrame(data_list, columns=["Inter-Arrival Time", "ID", "DLC", "Data", "Label"])
    df.to_csv(csv_file, index=False)
    print(f"File CSV đã được tạo: {csv_file}")

# Ví dụ sử dụng
parse_can_log("src/Attack_free_dataset.txt", "can_data_v5.csv")