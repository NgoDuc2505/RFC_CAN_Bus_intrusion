import pandas as pd
import joblib
import os

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

def detect_set_of_test(CSVlist, outputDir, output_file_name = "test_result_with_prediction.csv"):
    file_name = output_file_name.split(".")[0]
    isExist = not os.path.exists(outputDir) and not os.path.isdir(outputDir)
    if isExist:
        os.makedirs(outputDir)
        print(f"📁 Folder created: {outputDir}")
    else:
        print(f"📁 Folder already exists: {outputDir}")
    path = os.path.join(outputDir, output_file_name)

    df_test = pd.DataFrame()
    for csv_file in CSVlist:
        df_temp = pd.read_csv(csv_file)
        df_test = pd.concat([df_test, df_temp], ignore_index=True)

    df_test_processed = preprocess_data(df_test)

    model = joblib.load(model_file_path)

    X_test = df_test_processed[['timestamp', 'arbitration_id', 'data_field']]

    df_test['prediction'] = model.predict(X_test)
    df_test['is_equal'] = df_test['attack'] == df_test['prediction']
    if df_test['is_equal'].all():
        print("✅ Tất cả dự đoán đều chính xác.")
    else:
        print("❌ Có một số dự đoán không chính xác.")
        ratio = df_test["is_equal"].value_counts(normalize=True)
        print(ratio)
    with open(os.path.join(outputDir, f"{file_name}_logger.txt"), 'w') as f:
        for csv_file in CSVlist:
            f.write(f"files: {csv_file} \n")
        f.write(f"total: {len(df_test)} \n")
        f.write(ratio.to_string())
        f.write("\n")
    df_test.to_csv(path, index=False)
    print(f"✅ Dự đoán hoàn tất. File kết quả: {path}")

if __name__ == "__main__":
    # df_test = pd.read_csv(test_file_path4)

    # df_test_processed = preprocess_data(df_test)

    # model = joblib.load(model_file_path)

    # X_test = df_test_processed[['timestamp', 'arbitration_id', 'data_field']]

    # df_test['prediction'] = model.predict(X_test)

    # df_test.to_csv('test_result_with_prediction_balance4.csv', index=False)

    # print("✅ Dự đoán hoàn tất. File kết quả: test_result_with_prediction.csv")
    list_csv_test_01 = [
        "src/datasets/train_01/set_01/test_01_known_vehicle_known_attack/DoS-3.csv",
        "src/datasets/train_01/set_01/test_01_known_vehicle_known_attack/DoS-4.csv",
        "src/datasets/train_01/set_01/test_01_known_vehicle_known_attack/force-neutral-3.csv",
        "src/datasets/train_01/set_01/test_01_known_vehicle_known_attack/force-neutral-4.csv",
        "src/datasets/train_01/set_01/test_01_known_vehicle_known_attack/rpm-3.csv",
        "src/datasets/train_01/set_01/test_01_known_vehicle_known_attack/rpm-4.csv",
        "src/datasets/train_01/set_01/test_01_known_vehicle_known_attack/standstill-3.csv",
        "src/datasets/train_01/set_01/test_01_known_vehicle_known_attack/standstill-4.csv"
    ]
    list_csv_test_02 = [
        "src/datasets/train_01/set_01/test_02_unknown_vehicle_known_attack/DoS-3.csv",
        "src/datasets/train_01/set_01/test_02_unknown_vehicle_known_attack/DoS-4.csv",
        "src/datasets/train_01/set_01/test_02_unknown_vehicle_known_attack/force-neutral-3.csv",
        "src/datasets/train_01/set_01/test_02_unknown_vehicle_known_attack/force-neutral-4.csv",
        "src/datasets/train_01/set_01/test_02_unknown_vehicle_known_attack/rpm-3.csv",
        "src/datasets/train_01/set_01/test_02_unknown_vehicle_known_attack/rpm-4.csv",
        "src/datasets/train_01/set_01/test_02_unknown_vehicle_known_attack/standstill-3.csv",
        "src/datasets/train_01/set_01/test_02_unknown_vehicle_known_attack/standstill-4.csv"
    ]
    list_csv_test_03 = [
        "src/datasets/train_01/set_01/test_03_known_vehicle_unknown_attack/double-3.csv",
        "src/datasets/train_01/set_01/test_03_known_vehicle_unknown_attack/double-4.csv",
        "src/datasets/train_01/set_01/test_03_known_vehicle_unknown_attack/fuzzing-3.csv",
        "src/datasets/train_01/set_01/test_03_known_vehicle_unknown_attack/fuzzing-4.csv",
        "src/datasets/train_01/set_01/test_03_known_vehicle_unknown_attack/interval-3.csv",
        "src/datasets/train_01/set_01/test_03_known_vehicle_unknown_attack/interval-4.csv",
        "src/datasets/train_01/set_01/test_03_known_vehicle_unknown_attack/speed-3.csv",
        "src/datasets/train_01/set_01/test_03_known_vehicle_unknown_attack/speed-4.csv",
        "src/datasets/train_01/set_01/test_03_known_vehicle_unknown_attack/systematic-3.csv",
        "src/datasets/train_01/set_01/test_03_known_vehicle_unknown_attack/systematic-4.csv",
        "src/datasets/train_01/set_01/test_03_known_vehicle_unknown_attack/triple-3.csv",
        "src/datasets/train_01/set_01/test_03_known_vehicle_unknown_attack/triple-4.csv"
    ]
    list_csv_test_04 = [
        "src/datasets/train_01/set_01/test_04_unknown_vehicle_unknown_attack/double-3.csv",
        "src/datasets/train_01/set_01/test_04_unknown_vehicle_unknown_attack/double-4.csv",
        "src/datasets/train_01/set_01/test_04_unknown_vehicle_unknown_attack/fuzzing-3.csv",
        "src/datasets/train_01/set_01/test_04_unknown_vehicle_unknown_attack/fuzzing-4.csv",
        "src/datasets/train_01/set_01/test_04_unknown_vehicle_unknown_attack/interval-3.csv",
        "src/datasets/train_01/set_01/test_04_unknown_vehicle_unknown_attack/interval-4.csv",
        "src/datasets/train_01/set_01/test_04_unknown_vehicle_unknown_attack/speed-3.csv",
        "src/datasets/train_01/set_01/test_04_unknown_vehicle_unknown_attack/speed-4.csv",
        "src/datasets/train_01/set_01/test_04_unknown_vehicle_unknown_attack/systematic-3.csv",
        "src/datasets/train_01/set_01/test_04_unknown_vehicle_unknown_attack/systematic-4.csv",
        "src/datasets/train_01/set_01/test_04_unknown_vehicle_unknown_attack/triple-3.csv",
        "src/datasets/train_01/set_01/test_04_unknown_vehicle_unknown_attack/triple-4.csv"
    ]
    detect_set_of_test(list_csv_test_04, "src/test_result", output_file_name = "test_04_unknown_vehicle_unknown_attack.csv")