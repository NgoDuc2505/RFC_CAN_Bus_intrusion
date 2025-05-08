import joblib
import os
import pandas as pd
from sklearn.tree import _tree
import numpy as np

def analyze_tree(tree, feature_names, tree_id):
    tree_ = tree.tree_
    feature_name = [
        feature_names[i] if i != _tree.TREE_UNDEFINED else "N/A"
        for i in tree_.feature
    ]

    total_nodes = tree_.node_count
    leaf_nodes = 0
    pred_0 = 0
    pred_1 = 0

    for node_id in range(total_nodes):
        if tree_.feature[node_id] == _tree.TREE_UNDEFINED:
            leaf_nodes += 1
            prediction = np.argmax(tree_.value[node_id])
            if prediction == 0:
                pred_0 += 1
            elif prediction == 1:
                pred_1 += 1

    root_feature = feature_name[0]
    tree_depth = tree_.max_depth

    return {
        "Tree_ID": tree_id,
        "Total_Nodes": total_nodes,
        "Leaf_Nodes": leaf_nodes,
        "Tree_Depth": tree_depth,
        "Root_Feature": root_feature,
        "Leaf_Pred_1": pred_1,
        "Leaf_Pred_0": pred_0
    }

def summarize_forest(pkl_path, feature_names, output_csv="tree_summary.csv"):
    with open(pkl_path, 'rb') as file:
        model = joblib.load(file)

    summary = []

    for tree_id, estimator in enumerate(model.estimators_):
        info = analyze_tree(estimator, feature_names, tree_id)
        summary.append(info)

    df_summary = pd.DataFrame(summary)
    df_summary.to_csv(output_csv, index=False)
    print(f"📄 Đã lưu thống kê cây vào: {output_csv}")


if __name__ == "__main__":
    feature_names = ["timestamp", "arbitration_id", "data_field"]
    pkl_file = "datasets_release/model_candata_train_balance_set_v2.pkl"
    summarize_forest(pkl_file, feature_names, output_csv="datasets_release/tree_summary_v2.csv")
