import os
import struct
import pandas as pd
from collections import Counter

# ====================== CẤU HÌNH ======================
FEATURE_MAPPING = {
    0: 'arbitration_id',
    1: 'inter_arrival_time',
    10: 'data_entropy',
    11: 'dls',
    -1: 'none'
}

BIN_DIR = "src/LUT"
NUM_TREES = 49
# =======================================================

# ================== CHUYỂN ĐỔI CSV -> BIN ==============
def convert_csv_to_bin(csv_path, bin_path):
    """Chuyển đổi file CSV cây quyết định sang binary format"""
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()

    with open(bin_path, 'wb') as f:
        for _, row in df.iterrows():
            # Xử lý các giá trị
            node = int(row['Node'])
            feature = int(float(row['Feature'])) if not pd.isna(row['Feature']) else -1
            
            # Xử lý threshold
            threshold = float(row['Threshold']) if not pd.isna(row['Threshold']) else 0.0
            
            # Xử lý node con
            left = int(float(row['Left_Child'])) if not pd.isna(row['Left_Child']) else 0
            right = int(float(row['Right_Child'])) if not pd.isna(row['Right_Child']) else 0
            
            # Xử lý prediction (QUAN TRỌNG)
            pred_raw = str(row['Prediction']).strip()
            try:
                prediction = int(float(pred_raw))  # Chuyển về số nguyên
                if prediction == -1:
                    pass  # Nút trong
                elif prediction in (0, 1):
                    pass  # Nút lá
                else:
                    raise ValueError(f"Giá trị prediction không hợp lệ: {pred_raw}")
            except ValueError:
                if pred_raw.upper() == 'FF':
                    prediction = -1  # Coi 'FF' như -1
                else:
                    raise ValueError(f"Giá trị prediction không hợp lệ: {pred_raw}")

            # Đóng gói dữ liệu (12 bytes/node)
            packed = struct.pack(
                '<HifHHb',  # Format: uint16, int32, float32, uint16, uint16
                node,
                feature,
                threshold,
                left,
                right,
                prediction
            )
            # Thêm prediction (1 byte) và padding (3 bytes)
            packed += bytes(1) 
            f.write(packed)
    
    print(f"✅ Đã chuyển đổi {csv_path} -> {bin_path}")

def convert_all_csv_to_bin():
    """Chuyển đổi tất cả các file CSV trong thư mục"""
    for i in range(NUM_TREES):
        csv_path = os.path.join(BIN_DIR, f"tree_{i}.csv")
        bin_path = os.path.join(BIN_DIR, f"tree_{i}.bin")
        if os.path.exists(csv_path):
            convert_csv_to_bin(csv_path, bin_path)
        else:
            print(f"⚠️ File {csv_path} không tồn tại")
# =======================================================

# ================ ĐỌC VÀ DỰ ĐOÁN TỪ BIN ================
def load_bin_tree(bin_path):
    """Đọc cây nhị phân từ file với khung dữ liệu cố định 16 bytes/node"""
    nodes = {}
    with open(bin_path, 'rb') as f:
        while True:
            data = f.read(16)
            if not data or len(data) < 16:
                break

            # Giải mã 16 byte theo đúng định dạng
            node_id, feature, threshold, left, right, prediction = struct.unpack('<HifHHb', data[:15])
            
            nodes[node_id] = {
                'feature': feature,
                'threshold': threshold,
                'left': left,
                'right': right,
                'prediction': prediction
            }
    return nodes

def predict_from_bin_tree(tree_nodes, input_data, verbose=False):
    """Dự đoán từ một cây binary"""
    current_node = 0  # Bắt đầu từ node gốc
    
    while True:
        node = tree_nodes.get(current_node)
        if not node:
            if verbose:
                print(f"❌ Node {current_node} không tồn tại")
            return None
        
        # Nếu là nút lá (prediction khác -1)
        if node['prediction'] != -1:
            if verbose:
                print(f"✅ Node {current_node}: Prediction = {node['prediction']}")
            return node['prediction']
        
        # Lấy tên feature
        feature_name = FEATURE_MAPPING.get(node['feature'], 'unknown')
        feature_value = input_data.get(feature_name, float('nan'))
        
        if verbose:
            comp = "<=" if feature_value <= node['threshold'] else "> "
            print(f"🧠 Node {current_node}: {feature_name} ({feature_value:.5f}) {comp} {node['threshold']:.5f}")
        
        # Di chuyển đến node con
        current_node = node['left'] if feature_value <= node['threshold'] else node['right']

def vote_predictions_bin(bin_trees, input_data, verbose=False):
    """Dự đoán bằng voting từ nhiều cây binary"""
    predictions = []
    
    for tree_path in bin_trees:
        if verbose:
            print(f"\n=> Đang xử lý {os.path.basename(tree_path)}")
            
        tree_nodes = load_bin_tree(tree_path)
        pred = predict_from_bin_tree(tree_nodes, input_data, verbose)
        
        if pred is not None:
            predictions.append(pred)
        elif verbose:
            print("⚠️ Bỏ qua cây do lỗi dự đoán")
    
    if not predictions:
        return None, Counter()
    
    # Thực hiện voting
    prediction_counts = Counter(predictions)
    voted_prediction = prediction_counts.most_common(1)[0][0]
    
    return voted_prediction, prediction_counts
# =======================================================

# ====================== MAIN ===========================
if __name__ == "__main__":
    # Bước 1: Chuyển đổi tất cả CSV sang BIN (nếu cần)
    convert_all_csv_to_bin()
    
    # Bước 2: Chuẩn bị dữ liệu đầu vào
    sample_input = {
        'arbitration_id': 882, 'inter_arrival_time': 0.099141, 'data_entropy': 0.54356, 'dls': 8
    } #0
    
    # Bước 3: Tạo danh sách các file .bin
    bin_trees = [os.path.join(BIN_DIR, f"tree_{i}.bin") for i in range(NUM_TREES)]
    
    # Bước 4: Thực hiện dự đoán
    voted_pred, counts = vote_predictions_bin(bin_trees, sample_input, verbose=True)
    
    # Bước 5: Hiển thị kết quả
    print("\n" + "="*50)
    print(f"🧾 Kết quả dự đoán cuối cùng: {voted_pred} (0: Bình thường, 1: Tấn công)")
    print(f"📊 Thống kê vote: {dict(counts)}")
    print("="*50)


#3.123 - 3.12344234234 3.1232423423 

# 10