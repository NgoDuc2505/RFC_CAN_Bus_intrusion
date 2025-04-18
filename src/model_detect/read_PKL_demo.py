import pickle
import pandas as pd
import numpy as np
from sklearn.tree import _tree
import joblib
import os
from collections import defaultdict


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
    node_info["Tree"] = str(int(node_info['Tree']))
    node_info["Node"] = str(int(node_info['Node']))
    if node_info["Feature"] != "N/A":
        # Giữ nguyên giá trị threshold với 3 chữ số thập phân
        node_info["Threshold"] = f"{float(node_info['Threshold']):.5f}"
        node_info["Left_Child"] = str(int(node_info['Left_Child']))
        node_info["Right_Child"] = str(int(node_info['Right_Child']))
        node_info["Prediction"] = "-1"  # Giữ nguyên "FF" thành "255"
    else:
        node_info["Threshold"] = "0"
        node_info["Left_Child"] = "0"
        node_info["Right_Child"] = "0"
        node_info["Prediction"] = str(int(node_info['Prediction']))
        node_info["Feature"] = "-1"
    return node_info


def convert_and_save_each_tree_as_csv(pkl_path, output_folder, feature_names, mode="mem"):
    os.makedirs(output_folder, exist_ok=True)

    with open(pkl_path, 'rb') as file:
        model = joblib.load(file)

    # Process each tree individually and save as separate CSV files
    for tree_id, estimator in enumerate(model.estimators_):
        nodes = extract_tree_info(estimator, tree_id, feature_names, mode)
        df = pd.DataFrame(nodes)
        df = df[["Tree", "Node", "Feature", "Threshold", "Left_Child", "Right_Child", "Prediction"]]
        filename = f"tree_{tree_id}.csv"
        out_path = os.path.join(output_folder, filename)
        df.to_csv(out_path, index=False)
        print(f"✅ Đã lưu cây thứ {tree_id} vào {out_path}")


if __name__ == "__main__":
    feature_names = ["timestamp", "arbitration_id", "data_field"]
    feature_names_mapping = ["00", "01", "10"]
    pkl_file = "src/datasets_release/model_candata_train_balance_set.pkl"
    output_folder = "src/LUT/"

    convert_and_save_each_tree_as_csv(pkl_file, output_folder, feature_names_mapping, mode="mem")