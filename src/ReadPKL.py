import pickle
import joblib
import pandas as pd

# Load mô hình từ file .pkl
model_path = "RFC_CAN_Bus_intrusion/src/random_forest_model_v7_2.pkl"
model_loaded = joblib.load(model_path)

# Kiểm tra kiểu dữ liệu của mô hình
if not hasattr(model_loaded, "estimators_"):
    raise TypeError("❌ File .pkl không chứa một mô hình RandomForestClassifier hợp lệ.")

# Hàm chuyển đổi số thực thành nhị phân
def float_to_binary(value, scale=1000):
    """ Chuyển đổi giá trị số thực thành dạng nhị phân """
    if value == "N/A":
        return "N/A"
    int_value = int(value * scale)  # Nhân để giữ số thập phân
    return bin(int_value)[2:]  # Loại bỏ tiền tố '0b'

# Hàm chuyển đổi cây thành Look-Up Table (LUT)
def tree_to_lut(tree, tree_index):
    tree_structure = tree.tree_
    lut = []
    
    for node_id in range(tree_structure.node_count):
        if tree_structure.children_left[node_id] == -1 and tree_structure.children_right[node_id] == -1:
            # Nếu là node lá, lưu giá trị dự đoán
            lut.append({
                "Tree": tree_index,
                "Node": node_id,
                "Feature": "Leaf",
                "Threshold": "N/A",
                "Threshold_Binary": "N/A",
                "Left_Child": "N/A",
                "Right_Child": "N/A",
                "Prediction": tree_structure.value[node_id].argmax()
            })
        else:
            # Nếu không phải node lá, lưu điều kiện so sánh
            threshold = tree_structure.threshold[node_id]
            lut.append({
                "Tree": tree_index,
                "Node": node_id,
                "Feature": tree_structure.feature[node_id],
                "Threshold": threshold,
                "Threshold_Binary": float_to_binary(threshold),
                "Left_Child": tree_structure.children_left[node_id],
                "Right_Child": tree_structure.children_right[node_id],
                "Prediction": "N/A"
            })
    
    return lut

# Hàm lưu toàn bộ LUT vào CSV
def save_lut_to_csv(model, filename="lut_trees_binary.csv"):
    all_lut = []
    
    for i, tree in enumerate(model.estimators_):
        all_lut.extend(tree_to_lut(tree, i + 1))
    
    df = pd.DataFrame(all_lut)
    df.to_csv(filename, index=False)
    print(f"✅ LUT đã được lưu vào {filename}")

# Xuất LUT ra file CSV
save_lut_to_csv(model_loaded)
