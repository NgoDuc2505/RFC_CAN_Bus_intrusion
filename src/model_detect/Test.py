import csv
import os

# Danh sách dữ liệu mẫu
data_list = [
    ("1672531403.465987", "3E9", "133D1CDD1314190B"),
    ("1672531720.9798498", "184", "000300000000"),
    ("1672531305.6013842", "0AA", "2F042D9002526F00"),
    ("1672531242.356578", "25F", "CFC1CD2AB417"),
    ("1672531950.377639", "3F1", "00D25A181BFF005D"),
    ("1672531406.5422251", "199", "CFFF0FFFEFFE00FF"),
    ("1672531324.025028", "0AA", "2F042D9002526F00"),
    ("1672531377.902598", "0C1", "1109E9BE1176F23E"),
    ("1672531312.923432", "0AA", "2F042D9002526F00"),
    ("1672531613.022917", "0C5", "03CA94D500DEAB3A")
]

# Hàm chuyển các trường về nhị phân 64-bit
def convert_input_to_binary(timestamp, arbitration_id, data_field):
    timestamp_bin = format(int(float(timestamp)), '064b')
    arbitration_id_bin = format(int(arbitration_id, 16), '064b')
    data_field_bin = format(int(data_field, 16), '064b')
    return {
        'timestamp': timestamp_bin,
        'arbitration_id': arbitration_id_bin,
        'data_field': data_field_bin
    }

# Ghi ra file CSV bao gồm cả giá trị gốc và nhị phân
def convert_data_to_csv_with_binary(output_dir, filename):
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)

    with open(output_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            "timestamp", "arbitration_id", "data_field","attack"
        ])
        for timestamp, arbitration_id, data_field in data_list:
            bin_data = convert_input_to_binary(timestamp, arbitration_id, data_field)
            writer.writerow([
                bin_data['timestamp'], bin_data['arbitration_id'], bin_data['data_field'],'attack'
            ])

    print(f"✅ Đã tạo file CSV: '{output_path}'")

# Gọi hàm để xuất ra file
convert_data_to_csv_with_binary("LUT", "input_data_test.csv")

# import csv
# import os
# from collections import Counter

# # Hàm phân tích một dòng nhị phân 95 bit từ tệp .mif
# def parse_binary_row_95bit(bin_str):
#     assert len(bin_str) == 95, "Dòng nhị phân phải đúng 95 bit"
#     node        = int(bin_str[0:9], 2)
#     feature_bin = bin_str[9:11]
#     feature     = int(feature_bin, 2)
#     if feature_bin == '11':
#         feature = -1  # node lá
#     threshold   = int(bin_str[11:75], 2)
#     left_child  = int(bin_str[75:84], 2)
#     right_child = int(bin_str[84:93], 2)
#     prediction  = bin_str[93:95]  # chuỗi nhị phân
#     prediction_val = {'00': 0, '01': 1, '11': -1}.get(prediction, None)
#     return {
#         'Node': node,
#         'Feature': feature,
#         'Threshold': threshold,
#         'Left_Child': left_child,
#         'Right_Child': right_child,
#         'Prediction': prediction_val
#     }

# # Hàm tải cây quyết định từ tệp .mif
# def load_tree_from_mif(mif_path):
#     with open(mif_path, 'r') as f:
#         lines = f.readlines()
#     # Lọc dòng nhị phân 95 bit
#     data_lines = [line.strip() for line in lines
#                   if set(line.strip()) <= {'0', '1'} and len(line.strip()) == 95]
#     rows = [parse_binary_row_95bit(line) for line in data_lines]
#     return rows

# # Hàm dự đoán từ cây đã phân tích
# def predict_from_parsed_tree(tree_rows, input_data, verbose=False):
#     node = 0
#     input_bin = {
#         'timestamp':      input_data['timestamp'],
#         'arbitration_id': input_data['arbitration_id'],
#         'data_field':     input_data['data_field']
#     }
#     while True:
#         current = next((row for row in tree_rows if row['Node'] == node), None)
#         if current is None:
#             if verbose:
#                 print(f"❌ Node {node} không tồn tại.")
#             return None
#         if current['Feature'] == -1:
#             if verbose:
#                 print(f"Node {node} là lá → Prediction = {current['Prediction']}")
#             return current['Prediction']
#         feature_name = {0: 'timestamp', 1: 'arbitration_id', 2: 'data_field'}[current['Feature']]
#         threshold_bin = format(current['Threshold'], '064b')
#         print(f"Threshold bin tại node {node}: {threshold_bin}")  # ← in giá trị threshold_bin
#         input_value_bin = input_bin[feature_name]
#         if verbose:
#             print(f"\n-- Node {node} --")
#             print(f" Feature       : {feature_name} (code = {current['Feature']:02b})")
#             print(f" Input bits    : {input_value_bin}")
#             print(f" Threshold bits: {threshold_bin}")
#             cmp = "<=" if input_value_bin <= threshold_bin else " >"
#             print(f" So sánh: {input_value_bin} {cmp} {threshold_bin}")
#         if input_value_bin <= threshold_bin:
#             node = current['Left_Child']
#             if verbose:
#                 print(f" → Chọn Left_Child = {node}")
#         else:
#             node = current['Right_Child']
#             if verbose:
#                 print(f" → Chọn Right_Child = {node}")

# # Hàm bỏ phiếu dự đoán từ nhiều cây
# def vote_predictions_mif(trees, input_data, verbose=False):
#     predictions = []
#     for tree_path in trees:
#         if verbose:
#             print(f"\n📁 Đang xử lý cây: {tree_path}")
#         tree = load_tree_from_mif(tree_path)
#         pred = predict_from_parsed_tree(tree, input_data, verbose=verbose)
#         predictions.append(pred)
#     counts = Counter(predictions)
#     voted = counts.most_common(1)[0][0]
#     return voted, counts

# # Hàm đọc dữ liệu từ tệp CSV
# def read_input_data_from_csv(input_csv_path):
#     input_data_list = []
#     with open(input_csv_path, mode='r') as file:
#         reader = csv.DictReader(file)
#         for row in reader:
#             input_data_list.append({
#                 'timestamp': row['timestamp'],
#                 'arbitration_id': row['arbitration_id'],
#                 'data_field': row['data_field']
#             })
#     return input_data_list

# # Hàm xử lý tệp CSV và thực hiện dự đoán trên mỗi dòng
# def process_csv_and_predict(input_csv_path, trees):
#     input_data_list = read_input_data_from_csv(input_csv_path)
#     for idx, input_data in enumerate(input_data_list[:10]):  # Chỉ in 10 frame đầu
#         voted_pred, _ = vote_predictions_mif(trees, input_data, verbose=False)
#         label = "Attack" if voted_pred == 1 else "Normal"
#         print(f"Frame {idx} - {label}")

# if __name__ == "__main__":
#     trees = [f"LUT/tree_{i}_v.mif" for i in range(21)]
#     input_csv_path = "LUT/input_data.csv"
#     process_csv_and_predict(input_csv_path, trees)
