import pandas as pd
import struct

def convert_to_bin(sample = {
    'timestamp': 1672531398.7673929,
    'arbitration_id': '3E9',
    'data_field': "1B4C05111B511C69",
}):

    # Convert timestamp to 64-bit binary
    timestamp_bin = format(int(sample['timestamp']), '064b')

    # Convert arbitration_id (hex) to 11-bit binary
    arb_id_bin = format(int(sample['arbitration_id'], 16), '064b')

    # Convert data_field (hex string) to 64-bit binary
    data_bin = format(int(sample['data_field'], 16), '064b')

    # Label
    label_bin = '0'

    # Final binary line
    final_binary_line = timestamp_bin + arb_id_bin + data_bin + label_bin
    print(final_binary_line)
    print("Length:", len(final_binary_line))

def to_bin_64(val, is_hex=False):
    val = int(val, 16) if is_hex else int(val)
    return format(val, '064b')


def float_to_bin64_timestamp(value):
    packed = struct.pack('>d', value)
    return ''.join(f'{byte:08b}' for byte in packed)

def convert_sample_csv_to_bin(csv_path, out_path="src/binary_64bit_output.csv"):
    sample_count = 10
    df = pd.read_csv(csv_path)
    df_sample = df.head(sample_count)

    df_sample['timestamp'] = df_sample['timestamp'].apply(lambda x: float_to_bin64_timestamp(x))
    df_sample['arbitration_id'] = df_sample['arbitration_id'].apply(lambda x: to_bin_64(x, is_hex=True))
    df_sample['data_field'] = df_sample['data_field'].apply(lambda x: to_bin_64(x, is_hex=True))

    df_sample.to_csv(out_path, index=False)
    print(f"Đã chuyển đổi {sample_count} mẫu thành file {out_path}")

# def read


convert_sample_csv_to_bin("src/datasets/test_split_label/attack_only_set01_test01_Dos4_rpm4.csv", "binary_64bit_output_v2.csv")