import pandas as pd
import binascii
import re
import math

def hex_to_decimal(hex_string):
    return int(hex_string, 16)

def calculate_entropy(data_bytes):
    if not data_bytes:
        return 0
    
    freq = {byte: data_bytes.count(byte) / len(data_bytes) for byte in set(data_bytes)}
    entropy = -sum(p * math.log2(p) for p in freq.values())
    return round(entropy, 3)

def parse_can_log(txt_file, csv_file, label=0):
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
                
                
                data_decimals = [hex_to_decimal(byte) for byte in data_hex]
                
                
                data_entropy = calculate_entropy(data_decimals)
                
                
                inter_arrival_time = round((timestamp - prev_timestamp), 3) if prev_timestamp is not None else 0
                prev_timestamp = timestamp
                
                data_list.append([inter_arrival_time, arbitration_id, dlc, data_entropy, label])
    
    
    df = pd.DataFrame(data_list, columns=["Inter-Arrival Time", "ID", "DLC", "Data_Entropy", "Label"])
    df.to_csv(csv_file, index=False)
    print(f"File CSV đã được tạo: {csv_file}")


# parse_can_log("src/Attack_free_dataset.txt", "can_data_v6.csv")
# parse_can_log("src/DoS_attack_dataset.txt", "can_data_v6_DoS.csv", 1)
# parse_can_log("src/Fuzzy_attack_dataset.txt", "can_data_v6_Fuzzy.csv",1)
parse_can_log("src/Impersonation_attack_dataset.txt", "can_data_v6_Imper.csv",1)
