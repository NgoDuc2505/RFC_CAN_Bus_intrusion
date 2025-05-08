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

def encode_lut_line(tree, node, feature, threshold, left, right, predict):
    # Chuyển từng phần thành dạng phù hợp, scale lại nếu cần
    threshold_int = int(threshold) if isinstance(threshold, float) else threshold
    encoded = (tree << 56) | (node << 48) | (feature << 40) | (threshold_int << 24) | (left << 12) | (right << 0)
    if predict != -1:
        encoded |= (predict << 60)
    return f"{encoded:016X}"

    # with open("tree_weights.mif", "w") as f:
    #     f.write("WIDTH=64;\nDEPTH=512;\nADDRESS_RADIX=UNS;\nDATA_RADIX=HEX;\nCONTENT BEGIN\n")
    #     for i, row in enumerate(data_rows):
    #         line = encode_lut_line(*row)
    #         f.write(f"    {i} : {line};\n")
    #     f.write("END;\n")

def convert_lut_line_from_csv(dirLUT):
    file_list = os.listdir(dirLUT)
    csv_files = [f for f in file_list if f.endswith('.csv')]
    for i, file in enumerate(csv_files):
        file_path = os.path.join(dirLUT, file)
        df = pd.read_csv(file_path)
        print(f"Đang xử lý file {i + 1}/{len(csv_files)}: {file_path}")
        data_rows = []
        for index, row in df.iterrows():
            data_rows.append((int(row["Tree"]), int(row["Node"]), int(row["Feature"]), float(row["Threshold"]),
                              int(row["Left_Child"]), int(row["Right_Child"]), int(row["Prediction"])))

        with open(f"src/MIF2/tree_{i}_weights.mif", "w") as f:
            f.write("WIDTH=64;\nDEPTH=512;\nADDRESS_RADIX=UNS;\nDATA_RADIX=HEX;\nCONTENT BEGIN\n")
            for i, row in enumerate(data_rows):
                line = encode_lut_line(*row)
                f.write(f"    {i} : {line};\n")
            f.write("END;\n")

def convert_lut_line_from_csv_total(dirLUT):
    file_list = os.listdir(dirLUT)
    csv_files = [f for f in file_list if f.endswith('.csv')]
    output_name = "hex_total.mif"
    data_rows = []
    for i, file in enumerate(csv_files):
        file_path = os.path.join(dirLUT, file)
        df = pd.read_csv(file_path)
        print(f"Đang xử lý file {i + 1}/{len(csv_files)}: {file_path}")
        for index, row in df.iterrows():
            data_rows.append((int(row["Tree"]), int(row["Node"]), int(row["Feature"]), float(row["Threshold"]),
                              int(row["Left_Child"]), int(row["Right_Child"]), int(row["Prediction"])))

    with open(f"src/MIF2/{output_name}", "w") as f:
        f.write("WIDTH=64;\nDEPTH=512;\nADDRESS_RADIX=UNS;\nDATA_RADIX=HEX;\nCONTENT BEGIN\n")
        for i, row in enumerate(data_rows):
            line = encode_lut_line(*row)
            f.write(f"    {i} : {line};\n")
        f.write("END;\n")
    print(f"✅ Đã lưu file {output_name} vào src/MIF/{output_name} bao gồm {len(data_rows)} dòng.")


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

def check_dir(inputDir: str):
    isExist = not os.path.exists(inputDir) and not os.path.isdir(inputDir)
    if isExist:
        os.makedirs(inputDir)
        print(f"📁 Folder created: {inputDir}")
    else:
        print(f"📁 Folder already exists: {inputDir}")
    return isExist, inputDir

def merge_bin(dirBIN: str, outputDir: str):
    check_dir(outputDir)
    bin_files = ([f for f in os.listdir(dirBIN) if f.endswith('.bin')])
    output_file = os.path.join(outputDir, "bin_total.bin")
    with open(output_file, 'wb') as outfile:
        for file_name in bin_files:
            file_path = os.path.join(dirBIN, file_name)
            with open(file_path, 'rb') as infile:
                data = infile.read()
                outfile.write(data) 
    print("✅ Gộp file thành công:", output_file)

if __name__ == "__main__":
    # feature_names = ["timestamp", "arbitration_id", "data_field"]
    feature_names_mapping = ["00", "01", "10"]
    pkl_file = "src/model_release/model_candata_train_balance_set.pkl"
    output_folder = "src/LUT2/"

    # convert_and_save_each_tree_as_csv(pkl_file, output_folder, feature_names_mapping, mode="mem")
    # convert_lut_line_from_csv("src/LUT2")
    # convert_lut_line_from_csv_total("src/LUT2")
    # merge_bin("src/LUT2", "src/LUT2")