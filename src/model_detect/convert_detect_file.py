import csv

def convert_timestamp(ts_float):
    microseconds = int(float(ts_float) * 1_000_000)
    return f"0x{microseconds:016X}"

def convert_arbitration_id(arb_id):
    # Loại bỏ tiền tố "0x" nếu có, rồi chuyển sang int
    arb_int = int(arb_id, 16) if arb_id.startswith("0x") else int(arb_id, 16) if all(c in "0123456789ABCDEFabcdef" for c in arb_id) else int(arb_id)
    return f"0x{arb_int:016X}"

def convert_data_field(data):
    return f"0x{data.zfill(16).upper()}"

# Đường dẫn input/output
input_file = "datasets_release/set_03/test_02_unknown_vehicle_known_attack/triple-2.csv"
output_file = "datasets_release/set_03/test_02_unknown_vehicle_known_attack/converted_triple-2-1.csv"

with open(input_file, mode="r") as infile, open(output_file, mode="w", newline="") as outfile:
    reader = csv.DictReader(infile)
    writer = csv.writer(outfile)

    # Ghi tiêu đề cột
    writer.writerow(["timestamp", "arbitration_id", "data_field", "attack"])

    for row in reader:
        timestamp_hex = convert_timestamp(row["timestamp"])
        arbitration_id_hex = convert_arbitration_id(row["arbitration_id"])
        data_field_hex = convert_data_field(row["data_field"])
        attack = row.get("attack", "0")  # Nếu không có cột "attack" thì mặc định là "0"

        writer.writerow([timestamp_hex, arbitration_id_hex, data_field_hex, attack])

print(f"Đã chuyển đổi xong. File lưu tại: {output_file}")
