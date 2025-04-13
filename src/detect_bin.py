import os
import struct
import pandas as pd
from collections import Counter

# ====================== CẤU HÌNH ======================
FEATURE_MAPPING = {
    0x00: 'arbitration_id',
    0x01: 'inter_arrival_time',
    0x0A: 'data_entropy',
    0x0B: 'dls',
    0xFF: 'none'
}

BIN_DIR = "src/LUT"
NUM_TREES = 48  # Số lượng cây trong rừng
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
            feature = int(float(row['Feature'])) if not pd.isna(row['Feature']) else 0xFF
            
            # Xử lý threshold
            threshold = float(row['Threshold']) if not pd.isna(row['Threshold']) else 0.0
            
            # Xử lý node con
            left = int(float(row['Left_Child'])) if not pd.isna(row['Left_Child']) else 0
            right = int(float(row['Right_Child'])) if not pd.isna(row['Right_Child']) else 0
            
            # Xử lý prediction (QUAN TRỌNG)
            pred_raw = str(row['Prediction']).strip().upper()
            if pred_raw == 'FF':
                prediction = 0xFF  # 255 - Nút trong
            else:
                prediction = int(float(pred_raw))  # 0 hoặc 1 - Nút lá
                if prediction not in (0, 1):
                    raise ValueError(f"Giá trị prediction không hợp lệ: {pred_raw}")

            # Đóng gói dữ liệu (16 bytes/node)
            packed = struct.pack(
                '<HBfHHB',  # Format: uint16, uint8, float32, uint16, uint16, uint8
                node,
                feature,
                threshold,
                left,
                right,
                prediction
            )
            packed += bytes(4)  # Padding để đủ 16 bytes
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
    """Đọc và parse cây từ file binary"""
    nodes = {}
    with open(bin_path, 'rb') as f:
        while True:
            data = f.read(16)  # Mỗi node 16 bytes
            if not data or len(data) < 16:
                break
                
            # Giải mã struct
            node_id, feature, threshold, left, right, pred = struct.unpack('<HBfHHB', data[:12])
            
            nodes[node_id] = {
                'feature': feature,
                'threshold': threshold,
                'left': left,
                'right': right,
                'prediction': pred
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
        
        # Nếu là nút lá (prediction khác 0xFF)
        if node['prediction'] != 0xFF:
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
        'arbitration_id': 977,
        'inter_arrival_time': 0.02,
        'data_entropy': 1.549,
        'dls': 8,
    }
    
    # Bước 3: Tạo danh sách các file .bin
    bin_trees = [os.path.join(BIN_DIR, f"tree_{i}.bin") for i in range(NUM_TREES)]
    
    # Bước 4: Thực hiện dự đoán
    voted_pred, counts = vote_predictions_bin(bin_trees, sample_input, verbose=True)
    
    # Bước 5: Hiển thị kết quả
    print("\n" + "="*50)
    print(f"🧾 Kết quả dự đoán cuối cùng: {voted_pred} (0: Bình thường, 1: Tấn công)")
    print(f"📊 Thống kê vote: {dict(counts)}")
    print("="*50)