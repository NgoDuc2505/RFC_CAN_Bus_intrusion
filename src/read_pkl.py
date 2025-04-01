from sklearn.tree import export_text
import joblib
import matplotlib.pyplot as plt
from sklearn.tree import plot_tree

model_loaded = joblib.load("random_forest_model_v4_optimized.pkl")
print(type(model_loaded))
num_trees = len(model_loaded.estimators_)
print(f"Số lượng cây trong Random Forest: {num_trees}")
tree = model_loaded.estimators_[14]
tree_text = export_text(tree)
print(tree_text)

def plot_decision_tree(model, tree_index=0):
    """ Vẽ cây quyết định từ Random Forest """
    tree = model.estimators_[tree_index]  # Lấy một cây trong Random Forest

    plt.figure(figsize=(20, 10))
    plot_tree(tree, filled=True, feature_names=[f"feature_{i}" for i in range(tree.n_features_in_)])
    plt.title(f"Decision Tree số {tree_index + 1} trong Random Forest")
    plt.show()


# plot_decision_tree(model_loaded, tree_index=0)