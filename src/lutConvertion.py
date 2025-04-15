import pickle
import pandas as pd
import numpy as np
from sklearn.tree import _tree
import joblib


def extract_tree_info(tree, tree_id, feature_names, mode="mem"):
    tree_ = tree.tree_
    feature_name = [
        feature_names[i] if i != _tree.TREE_UNDEFINED else "N/A"
        for i in tree_.feature
    ]
    nodes = []

    
    for node_id in range(tree_.node_count):
        node_info = {
            "Tree": tree_id,
            "Node": node_id,
            "Feature": feature_name[node_id],
            "Threshold": tree_.threshold[node_id],
            "Left_Child": tree_.children_left[node_id],
            "Right_Child": tree_.children_right[node_id],
            "Prediction": np.nan  
        }

        if node_info["Feature"] == "N/A":
            node_info["Threshold"] = np.nan
            node_info["Left_Child"] = np.nan
            node_info["Right_Child"] = np.nan
            node_info["Prediction"] = np.argmax(tree_.value[node_id])
        else:
            node_info["Prediction"] = np.nan
        
        if mode == "mem":
            node_info = convertNodeToMemFile(node_info)

        nodes.append(node_info)
    
    return nodes

def convertNodeToMemFile(node_info: dict[str, any]) -> dict[str, any]:
    node_info["Tree"] = f"{int(node_info["Tree"]):02x}"
    node_info["Node"] = f"{int(node_info["Node"]):02x}"
    if(node_info["Feature"] != "N/A"):
        # node_info["Threshold"] =  f"{int(float(node_info["Threshold"]) * (2**16)):08x}" #32bit
        node_info["Threshold"] =  f"{int(float(node_info["Threshold"]) * (2**8)):04x}" #16bit
        node_info["Left_Child"] = f"{int(node_info["Left_Child"]):02x}"
        node_info["Right_Child"] = f"{int(node_info["Right_Child"]):02x}"
        node_info["Prediction"] = "FF"
    else:
        node_info["Threshold"] = "FF"
        node_info["Left_Child"] = "FF"
        node_info["Right_Child"] = "FF"
        node_info["Prediction"] = f"{int(node_info["Prediction"]):02x}"
        node_info["Feature"] = "FF"
    return node_info
    


def convert_pkl_to_csv(pkl_path, csv_path, feature_names, mode="mem"):
    
    with open(pkl_path, 'rb') as file:
        model = joblib.load(file)
    
    all_nodes = []
   
    for tree_id, estimator in enumerate(model.estimators_):
        nodes = extract_tree_info(estimator, tree_id, feature_names, mode)
        all_nodes.extend(nodes)
    

    df = pd.DataFrame(all_nodes)
    
    # Định dạng lại cột
    # df["Threshold"] = df["Threshold"].apply(lambda x: f"{x:.6f}" if not np.isnan(x) else "N/A")
    # df["Left_Child"] = df["Left_Child"].apply(lambda x: int(x) if not np.isnan(x) else "N/A")
    # df["Right_Child"] = df["Right_Child"].apply(lambda x: int(x) if not np.isnan(x) else "N/A")
    # df["Prediction"] = df["Prediction"].apply(lambda x: int(x) if not np.isnan(x) else "N/A")
    
    # Sắp xếp cột theo yêu cầu
    df = df[["Tree", "Node", "Feature", "Threshold", "Left_Child", "Right_Child", "Prediction"]]
    
    # Lưu vào .csv
    df.to_csv(csv_path, index=False)
    print(f"Đã lưu file .csv vào {csv_path}")
if __name__ == "__main__":
    feature_names =         ["A_ID", "T_A", "D_E", "DLS"]
    feature_names_mapping = ["00", "01", "10", "11"]
    pkl_file = "random_forest_model_v4_lite_17ts.pkl"  
    csv_file = "src/random_forest_model_v4_lite_17ts_LUT.csv"      
    
    
    convert_pkl_to_csv(pkl_file, csv_file, feature_names_mapping, mode="mem")