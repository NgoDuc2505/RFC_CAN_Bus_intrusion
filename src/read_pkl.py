import pickle

# Load model từ file .pkl
with open("random_forest_model_v2.pkl", "rb") as model_file:
    model = pickle.load(model_file)

# Kiểm tra nội dung mô hình
print(model)