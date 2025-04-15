import pandas as pd
import re
import math

def hex_to_decimal(hex_string):
    """Chuyển đổi số hex sang số nguyên"""
    return int(hex_string, 16)

def calculate_entropy(data_bytes):
    """Tính entropy của dữ liệu"""
    if not data_bytes:
        return 0

    freq = {byte: data_bytes.count(byte) / len(data_bytes) for byte in set(data_bytes)}
    entropy = -sum(p * math.log2(p) for p in freq.values())
    return round(entropy, 3)

def parse_can_log(txt_file, csv_file):
    data_list = []
    prev_timestamp = None

    # Định dạng regex phù hợp với dữ liệu của bạn
    pattern = re.compile(r'\((\d+\.\d+)\)\s+can0\s+([0-9A-Fa-f]+)#([0-9A-Fa-f]+)')

    with open(txt_file, 'r') as file:
        for line in file:
            match = pattern.search(line)
            if match:
                timestamp = float(match.group(1))  # Timestamp
                arbitration_id = hex_to_decimal(match.group(2))  # ID (Hex → Decimal)
                data_hex = match.group(3)  # Dữ liệu dạng hex

                # Chuyển đổi dữ liệu hex thành danh sách số nguyên
                data_decimals = [hex_to_decimal(data_hex[i:i+2]) for i in range(0, len(data_hex), 2)]

                # Tính entropy của dữ liệu
                data_entropy = calculate_entropy(data_decimals)

                # Tính khoảng thời gian giữa các gói tin
                inter_arrival_time = round((timestamp - prev_timestamp), 3) if prev_timestamp is not None else 0
                prev_timestamp = timestamp

                # DLC là độ dài của chuỗi dữ liệu chia cho 2 (vì mỗi byte có 2 ký tự hex)
                dlc = len(data_decimals)

                # Label luôn bằng 0 = ko attack
                label = 1

                # Thêm vào danh sách dữ liệu
                data_list.append([inter_arrival_time, arbitration_id, dlc, data_entropy, label])

    # Chuyển đổi thành DataFrame và lưu vào CSV
    df = pd.DataFrame(data_list, columns=["Inter-Arrival Time", "ID", "DLC", "Data_Entropy", "Label"])
    df.to_csv(csv_file, index=False)
    print(f"File CSV đã được tạo: {csv_file}")
"""
# Gọi hàm với tập dữ liệu của bạn
parse_can_log("src/dataset_v2/extra-attack-free-1.log", "src/dataset_v2/can-data-v6-extra-attack-free-1.csv")
parse_can_log("src/dataset_v2/extra-attack-free-2.log", "src/dataset_v2/can-data-v6-extra-attack-free-2.csv")
parse_can_log("src/dataset_v2/extra-attack-free-3.log", "src/dataset_v2/can-data-v6-extra-attack-free-3.csv")
parse_can_log("src/dataset_v2/extra-attack-free-4.log", "src/dataset_v2/can-data-v6-extra-attack-free-4.csv")
parse_can_log("src/dataset_v2/extra-attack-free-5.log", "src/dataset_v2/can-data-v6-extra-attack-free-5.csv")
parse_can_log("src/dataset_v2/extra-attack-free-6.log", "src/dataset_v2/can-data-v6-extra-attack-free-6.csv")
parse_can_log("src/dataset_v2/extra-attack-free-7.log", "src/dataset_v2/can-data-v6-extra-attack-free-7.csv")
parse_can_log("src/dataset_v2/extra-attack-free-8.log", "src/dataset_v2/can-data-v6-extra-attack-free-8.csv")


"""

parse_can_log("src/dataset_v2/force-neutral-1.log", "src/dataset_v2/can-data-v6-force-neutral-1.csv")
parse_can_log("src/dataset_v2/force-neutral-2.log", "src/dataset_v2/can-data-v6-force-neutral-2.csv")
parse_can_log("src/dataset_v2/force-neutral-3.log", "src/dataset_v2/can-data-v6-force-neutral-3.csv")
parse_can_log("src/dataset_v2/force-neutral-4.log", "src/dataset_v2/can-data-v6-force-neutral-4.csv")

parse_can_log("src/dataset_v2/interval-1.log", "src/dataset_v2/can-data-v6-interval-1.csv")
parse_can_log("src/dataset_v2/interval-2.log", "src/dataset_v2/can-data-v6-interval-2.csv")
parse_can_log("src/dataset_v2/interval-3.log", "src/dataset_v2/can-data-v6-interval-3.csv")
parse_can_log("src/dataset_v2/interval-4.log", "src/dataset_v2/can-data-v6-interval-4.csv")

parse_can_log("src/dataset_v2/rpm-1.log", "src/dataset_v2/can-data-v6-rpm-1.csv")
parse_can_log("src/dataset_v2/rpm-2.log", "src/dataset_v2/can-data-v6-rpm-2.csv")
parse_can_log("src/dataset_v2/rpm-3.log", "src/dataset_v2/can-data-v6-rpm-3.csv")
parse_can_log("src/dataset_v2/rpm-4.log", "src/dataset_v2/can-data-v6-rpm-4.csv")

parse_can_log("src/dataset_v2/rpm-accessory-1.log", "src/dataset_v2/can-data-v6-rpm-accessory-1.csv")
parse_can_log("src/dataset_v2/rpm-accessory-2.log", "src/dataset_v2/can-data-v6-rpm-accessory-2.csv")
parse_can_log("src/dataset_v2/rpm-accessory-3.log", "src/dataset_v2/can-data-v6-rpm-accessory-3.csv")
parse_can_log("src/dataset_v2/rpm-accessory-4.log", "src/dataset_v2/can-data-v6-rpm-accessory-4.csv")

parse_can_log("src/dataset_v2/speed-1.log", "src/dataset_v2/can-data-v6-speed-1.csv")
parse_can_log("src/dataset_v2/speed-2.log", "src/dataset_v2/can-data-v6-speed-2.csv")
parse_can_log("src/dataset_v2/speed-3.log", "src/dataset_v2/can-data-v6-speed-3.csv")
parse_can_log("src/dataset_v2/speed-4.log", "src/dataset_v2/can-data-v6-speed-4.csv")

parse_can_log("src/dataset_v2/speed-accessory-1.log", "src/dataset_v2/can-data-v6-speed-accessory-1.csv")
parse_can_log("src/dataset_v2/speed-accessory-2.log", "src/dataset_v2/can-data-v6-speed-accessory-2.csv")
parse_can_log("src/dataset_v2/speed-accessory-3.log", "src/dataset_v2/can-data-v6-speed-accessory-3.csv")
parse_can_log("src/dataset_v2/speed-accessory-4.log", "src/dataset_v2/can-data-v6-speed-accessory-4.csv")

parse_can_log("src/dataset_v2/standstill-1.log", "src/dataset_v2/can-data-v6-standstill-1.csv")
parse_can_log("src/dataset_v2/standstill-2.log", "src/dataset_v2/can-data-v6-standstill-2.csv")
parse_can_log("src/dataset_v2/standstill-3.log", "src/dataset_v2/can-data-v6-standstill-3.csv")
parse_can_log("src/dataset_v2/standstill-4.log", "src/dataset_v2/can-data-v6-standstill-4.csv")


