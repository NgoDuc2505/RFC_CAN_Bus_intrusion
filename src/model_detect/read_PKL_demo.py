import pickle
import pandas as pd
import numpy as np
from sklearn.tree import _tree
import joblib
import os
import struct
from typing import List, Dict, Any

class TreeExtractor:
    def __init__(self, feature_names: List[str], feature_mapping: List[str]):
        self.feature_names = feature_names
        self.feature_mapping = feature_mapping
    
    def float_to_hex64(self, f: float) -> str:
        """Convert float to 64-bit hexadecimal IEEE 754 representation"""
        try:
            packed = struct.pack('!d', f)
            hex_str = ''.join(f'{byte:02x}' for byte in packed)
            return '0x' + hex_str.upper()
        except (struct.error, TypeError):
            return '0x0000000000000000'
    
    def extract_tree_info(self, tree, tree_id: int, mode: str = "mem") -> List[Dict[str, Any]]:
        """Extract information from a single decision tree"""
        tree_ = tree.tree_
        nodes = []
        
        for node_id in range(tree_.node_count):
            feature_idx = tree_.feature[node_id]
            feature_name = (
                self.feature_mapping[feature_idx] 
                if feature_idx != _tree.TREE_UNDEFINED 
                else "N/A"
            )
            
            node_info = {
                "Tree": tree_id,
                "Node": node_id,
                "Feature": feature_name,
                "Threshold": tree_.threshold[node_id],
                "Left_Child": tree_.children_left[node_id],
                "Right_Child": tree_.children_right[node_id],
                "Prediction": np.nan,
                "Threshold_Hex64": "0x0000000000000000"  # Initialize hex field
            }
            
            if feature_name == "N/A":  # Leaf node
                node_info.update({
                    "Threshold": np.nan,
                    "Left_Child": np.nan,
                    "Right_Child": np.nan,
                    "Prediction": np.argmax(tree_.value[node_id])
                })
            else:  # Decision node
                node_info["Threshold_Hex64"] = self.float_to_hex64(node_info["Threshold"])
            
            if mode == "mem":
                node_info = self.convert_node_to_mem_format(node_info)
            
            nodes.append(node_info)
        
        return nodes
    
    def convert_node_to_mem_format(self, node_info: Dict[str, Any]) -> Dict[str, Any]:
        """Convert node information to memory-friendly format"""
        converted = {
            "Tree": str(int(node_info['Tree'])),
            "Node": str(int(node_info['Node'])),
            "Feature": "-1" if node_info["Feature"] == "N/A" else node_info["Feature"],
            "Threshold": "0" if node_info["Feature"] == "N/A" else f"{float(node_info['Threshold']):.5f}",
            "Left_Child": "0" if node_info["Feature"] == "N/A" else str(int(node_info['Left_Child'])),
            "Right_Child": "0" if node_info["Feature"] == "N/A" else str(int(node_info['Right_Child'])),
            "Prediction": str(int(node_info['Prediction'])) if node_info["Feature"] == "N/A" else "-1",
            "Threshold_Hex64": node_info["Threshold_Hex64"]
        }
        return converted
    
    def process_model(self, model, output_folder: str, mode: str = "mem"):
        """Process all trees in the model"""
        os.makedirs(output_folder, exist_ok=True)
        
        for tree_id, estimator in enumerate(model.estimators_):
            nodes = self.extract_tree_info(estimator, tree_id, mode)
            df = pd.DataFrame(nodes)
            
            # Select and order columns
            columns = [
                "Node", "Feature", 
                "Threshold_Hex64", "Left_Child", 
                "Right_Child", "Prediction"
            ]
            df = df[columns]
            
            # Save to CSV
            filename = f"tree_{tree_id}_v.csv"
            out_path = os.path.join(output_folder, filename)
            df.to_csv(out_path, index=False)
            print(f"✅ Successfully saved tree {tree_id} to {out_path}")


def main():
    # Configuration
    FEATURE_NAMES = ["timestamp", "arbitration_id", "data_field"]
    FEATURE_MAPPING = ["00", "01", "10"]
    MODEL_PATH = "datasets_release/model_candata_train_balance_set_v5.pkl"
    OUTPUT_FOLDER = "LUT/"
    
    try:
        # Initialize extractor
        extractor = TreeExtractor(FEATURE_NAMES, FEATURE_MAPPING)
        
        # Load model
        with open(MODEL_PATH, 'rb') as file:
            model = joblib.load(file)
        
        # Process model
        extractor.process_model(model, OUTPUT_FOLDER, mode="mem")
        
    except FileNotFoundError:
        print(f"❌ Error: Model file not found at {MODEL_PATH}")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {str(e)}")


if __name__ == "__main__":
    main()