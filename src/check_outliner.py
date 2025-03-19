import numpy as np
from scipy import stats

def check_outliner(df):
    Q1 = df["Data_Entropy"].quantile(0.25)
    Q3 = df["Data_Entropy"].quantile(0.75)
    IQR = Q3 - Q1

    # Ngưỡng outlier
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    # Lọc các outlier
    outliers = df[(df["Data_Entropy"] < lower_bound) | (df["Data_Entropy"] > upper_bound)]
    print(f"Số lượng outlier (irq): {len(outliers)}")


    z_scores = np.abs(stats.zscore(df["Data_Entropy"]))
    outliers = df[z_scores > 3]
    print(f"Số lượng outlier (zscore): {len(outliers)}")