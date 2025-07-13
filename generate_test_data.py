import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

# ====== Load rainfall dataset ======
data = pd.read_csv("data/bgd-rainfall-adm2-full.csv", low_memory=False)

# ====== Preprocessing ======
data['date'] = pd.to_datetime(data['date'], errors='coerce')
data['rfh'] = pd.to_numeric(data['rfh'], errors='coerce')
data = data.dropna(subset=['date', 'rfh'])

data['year'] = data['date'].dt.year
data['month'] = data['date'].dt.month
data['quarter'] = data['date'].dt.quarter
data['is_monsoon'] = data['month'].apply(lambda x: 1 if x in [6, 7, 8, 9] else 0)

# ====== Add season info ======
season_mapping = {
    12: "Winter", 1: "Winter", 2: "Winter",
    3: "Summer", 4: "Summer", 5: "Summer",
    6: "Monsoon", 7: "Monsoon", 8: "Monsoon", 9: "Monsoon",
    10: "Post-Monsoon", 11: "Post-Monsoon"
}
data['season'] = data['month'].map(season_mapping)

# ====== Lag, rolling, diff features ======
data['rfh_lag1'] = data.groupby('ADM2_PCODE')['rfh'].shift(1)
data['rfh_lag2'] = data.groupby('ADM2_PCODE')['rfh'].shift(2)
data['rfh_roll3'] = data.groupby('ADM2_PCODE')['rfh'].rolling(3).mean().reset_index(0, drop=True)
data['rfh_roll6'] = data.groupby('ADM2_PCODE')['rfh'].rolling(6).mean().reset_index(0, drop=True)
data['rfh_diff'] = data.groupby('ADM2_PCODE')['rfh'].diff()

# ====== Advanced Features ======
data['sin_month'] = np.sin(2 * np.pi * data['month'] / 12)
data['cos_month'] = np.cos(2 * np.pi * data['month'] / 12)
data['month_avg_rfh'] = data.groupby('month')['rfh'].transform('mean')
data['time_idx'] = range(len(data))

# ====== Drop missing values ======
data = data.dropna()

# ====== One-hot encoding for season ======
data = pd.get_dummies(data, columns=['season'], drop_first=True)

# ====== Auto-select district with enough rows ======
district_counts = data['ADM2_PCODE'].value_counts()
selected_district = None

for code, count in district_counts.items():
    if count >= 100:
        selected_district = code
        break

if not selected_district:
    print("❌ No district has enough data after feature engineering.")
    exit()

data = data[data['ADM2_PCODE'] == selected_district]
print(f"✅ Selected district: {selected_district} with {len(data)} rows")

# ====== Ensure required season columns ======
for col in ['season_Monsoon', 'season_Post-Monsoon', 'season_Summer']:
    if col not in data.columns:
        data[col] = 0

# ====== Final 16 Features ======
selected_features = [
    'year', 'month', 'quarter', 'is_monsoon',
    'rfh_lag1', 'rfh_lag2', 'rfh_roll3', 'rfh_roll6', 'rfh_diff',
    'sin_month', 'cos_month', 'month_avg_rfh', 'time_idx',
    'season_Monsoon', 'season_Post-Monsoon', 'season_Summer'
]

# ====== Ensure all features are string-named (for XGBoost) ======
data.rename(columns={col: str(col) for col in data.columns}, inplace=True)
selected_features = list(map(str, selected_features))

X = data[selected_features]
y = data['rfh']

# ====== Train-Test Split ======
if len(X) < 10:
    print("⚠️ Not enough data to split. Saving all as test set.")
    test_data = X.copy()
    test_data['rfh'] = y
    test_data['date'] = data['date'].values  # ✅ Needed for Prophet
else:
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
    test_data = X_test.copy()
    test_data['rfh'] = y_test
    test_data['date'] = data.loc[X_test.index, 'date']  # ✅ Add date for Prophet

# ====== Save CSV ======
test_data.to_csv("data/test_data.csv", index=False)
print("✅ test_data.csv saved with 16 features + rfh + date.")
print("📊 Features:", test_data.columns.tolist())
