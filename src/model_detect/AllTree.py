import joblib
import os
import pandas as pd
from sklearn.tree import _tree

def analyze_forest_summary(pkl_path, feature_names, output_csv):
    with open(pkl_path, 'rb') as file:
        model = joblib.load(file)

    summary = []
    root_features = []

    for i, estimator in enumerate(model.estimators_):
        tree_ = estimator.tree_
        total_nodes = tree_.node_count
        internal_nodes = 0
        one_child_nodes = 0
        leaf_nodes = 0

        for node_id in range(tree_.node_count):
            left = tree_.children_left[node_id]
            right = tree_.children_right[node_id]

            if left == _tree.TREE_LEAF and right == _tree.TREE_LEAF:
                leaf_nodes += 1
            elif left == _tree.TREE_LEAF or right == _tree.TREE_LEAF:
                one_child_nodes += 1
                internal_nodes += 1
            else:
                internal_nodes += 1

        root_feature_idx = tree_.feature[0]
        root_feature = (
            feature_names[root_feature_idx]
            if root_feature_idx != _tree.TREE_UNDEFINED
            else "N/A"
        )
        root_features.append(root_feature)

        summary.append({
            "CÂY": i,
            "tổng số node": total_nodes,
            "số node con": internal_nodes,
            "số node con = 1": one_child_nodes,
            "số node con = 0": leaf_nodes,
            "feature ở root node đầu tiên": root_feature,
        })

    df_summary = pd.DataFrame(summary)

    # Đếm số lần mỗi feature xuất hiện ở root node
    root_counts = {feat: root_features.count(feat) for feat in feature_names}
    total_row = {
        "CÂY": "TỔNG",
        "tổng số node": "",
        "số node con": "",
        "số node con = 1": "",
        "số node con = 0": "",
        "feature ở root node đầu tiên": str(root_counts)
    }

    df_summary.loc[len(df_summary)] = total_row
    df_summary.to_csv(output_csv, index=False)
    print(f"📄 Đã lưu thống kê vào {output_csv}")

if __name__ == "__main__":
    feature_names = ["A_ID", "T_A", "D_E", "DLS"]
    pkl_path = "src/datasets_release/random_forest_model_v5_lite.pkl"
    output_csv = "src/LUT/forest_summary.csv"

    analyze_forest_summary(pkl_path, feature_names, output_csv)
