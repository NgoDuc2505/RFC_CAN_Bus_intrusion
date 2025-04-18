import pandas as pd
import joblib


def convert_timestamp(ts):
    try:
        return float(ts)
    except:
        return 0.0


def preprocess_data(df):
    df = df.copy()
    df['timestamp'] = df['timestamp'].apply(convert_timestamp)
    for col in ['arbitration_id', 'data_field']:
        if df[col].dtype == object:
            df[col] = df[col].apply(lambda x: int(x, 16) if isinstance(x, str) else x)
    return df

# Đường dẫn file
test_file_path = 'src/datasets/train_01/set_04/test_01_known_vehicle_known_attack/speed-accessory-1.csv'                
test_file_path2 = 'src/datasets/train_01/set_02/test_01_known_vehicle_known_attack/fuzzing-4.csv'                
test_file_path3 = 'src/datasets/train_01/set_04/test_03_known_vehicle_unknown_attack/DoS-1.csv'                
test_file_path4 = 'src/datasets/train_01/set_01/test_01_known_vehicle_known_attack/DoS-4.csv'                
model_file_path = 'src/model_release/model_candata_train_balance_set.pkl'     

# Đọc file CSV
df_test = pd.read_csv(test_file_path4)

# Tiền xử lý
df_test_processed = preprocess_data(df_test)

# Tải model
model = joblib.load(model_file_path)

# Lấy các features phù hợp
X_test = df_test_processed[['timestamp', 'arbitration_id', 'data_field']]

# Dự đoán
df_test['prediction'] = model.predict(X_test)

# Lưu kết quả
df_test.to_csv('test_result_with_prediction_balance4.csv', index=False)

print("✅ Dự đoán hoàn tất. File kết quả: test_result_with_prediction.csv")