import struct

def float_to_bin(value):
    # Chuyển đổi số thực thành nhị phân 64-bit theo chuẩn IEEE 754
    return format(struct.unpack('!Q', struct.pack('!d', value))[0], '064b')

def convert_csv_to_mif(csv_file, mif_file):
    with open(csv_file, 'r') as csv, open(mif_file, 'w') as mif:
        
        # Bỏ qua dòng tiêu đề của CSV
        next(csv)
        
        # Xử lý từng dòng trong CSV
        for line in csv:
            # Tách dữ liệu từ mỗi dòng
            node, feature, threshold, left_child, right_child, prediction = line.strip().split(',')
            
            # Chuyển đổi Node
            node_bin = format(int(node), '09b')
            
            # Xử lý Feature
            if feature == '-1':
                feature_bin = '11'  # Nếu feature = -1 thì chuyển thành '11'
                threshold_bin = '0' * 64  # Đặt threshold thành 64 bit 0
            else:
                feature_bin = format(int(feature, 2), '02b')  # Các trường hợp khác vẫn chuyển nhị phân 2 bi
                # Nếu Feature không phải "01" hoặc "-1", chuyển Threshold thành nhị phân 64-bit của số nguyên
                threshold_bin = format(int(float(threshold)), '064b')
            
            # Chuyển đổi Left và Right Child
            left_bin = format(int(left_child), '09b')
            right_bin = format(int(right_child), '09b')
            
            # Chuyển đổi Prediction
            if int(prediction) == -1:
                prediction_bin = '11'
            elif int(prediction) == 1:
                prediction_bin = '01'
            else:
                prediction_bin = '00'
            
            # Ghép các trường lại thành một chuỗi nhị phân
            # data_bin = node_bin+"|" + feature_bin+"|"  + threshold_bin+"|"  + left_bin +"|" + right_bin+"|"  + prediction_bin
            
            data_bin = node_bin + feature_bin + threshold_bin + left_bin + right_bin + prediction_bin
            # Ghi dữ liệu vào file MIF
            mif.write(f"{data_bin}\n")
        
      

# Lặp qua các tree_id từ 0 đến 20 và chuyển đổi từng file CSV thành MIF
for tree_id in range(21):
    csv_file = f'LUT/tree_{tree_id}_v.csv'
    mif_file = f'LUT/tree_{tree_id}_v.mif'
    convert_csv_to_mif(csv_file, mif_file)
    print(f"Đã chuyển {csv_file} thành {mif_file}")
