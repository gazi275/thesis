import streamlit as st
import pandas as pd
import numpy as np
import joblib
import geopandas as gpd
import plotly.express as px
from datetime import datetime, timedelta
from sklearn.metrics import mean_absolute_error, mean_squared_error

# 💅 CSS
st.markdown("""
<style>
.stApp {
    background-color: #f0f8ff;
}
.title {
    font-size: 42px;
    font-weight: 700;
    text-align: center;
    margin-bottom: 30px;
    background: linear-gradient(90deg, #2c3e50, #3498db);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
}
label, .stRadio > div, .stSelectbox > div {
    color: #2c3e50 !important;
    font-weight: 800;
    font-size: 22px !important;
}
.metric-container {
    background: white;
    padding: 20px 15px;
    border-radius: 10px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    margin: 10px 0 30px;
    border-left: 5px solid #1abc9c;
    color: #2c3e50;
}
.stMetric label, .stMetric div {
    color: #2c3e50 !important;
}
.plot-container {
    border: 2px solid #3498db;
    border-radius: 12px;
    padding: 10px;
    background: white;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    margin-bottom: 20px;
}
.footer {
    text-align: center;
    color: #7f8c8d;
    font-size: 14px;
    margin-top: 30px;
    padding-top: 15px;
    border-top: 2px solid #ecf0f1;
    font-style: italic;
}
.stSelectbox > div, .stRadio > div {
    background: #ffffff !important;
    border-radius: 6px;
    padding: 10px;
}
</style>
""", unsafe_allow_html=True)

# <!-- DESIGN: Title Section -->
st.markdown('<div class="title">🌧️ Rainfall Forecast Dashboard</div>', unsafe_allow_html=True)

# <!-- DESIGN: Sidebar Selections -->
col1, col2 = st.columns([1, 1])
with col1:
    # <!-- DESIGN: District Selection Dropdown -->
    @st.cache_data
    def load_districts():
        try:
            df = pd.read_csv("data/bgd-rainfall-adm2-full.csv")
            if "ADM2_EN" not in df.columns:
                gdf = gpd.read_file("data/adm2Shape/bgd_admbnda_adm2_bbs_20201113.shp")
                df = df.merge(gdf[['ADM2_PCODE', 'ADM2_EN']], on='ADM2_PCODE', how='left')
            return sorted(df['ADM2_EN'].dropna().unique())
        except Exception as e:
            st.error(f"Error loading districts: {e}")
            return []
    districts = load_districts()
    district = st.selectbox("🌍 Select District", districts, index=districts.index("Dhaka") if "Dhaka" in districts else 0)
with col2:
    # <!-- DESIGN: Model Selection Multiselect -->
    @st.cache_resource
    def load_models():
        try:
            model_paths = {
                "XGBoost": "xgb_model.pkl",
                "Random Forest": "rf_model.pkl",
                "LightGBM": "lgbm_model.pkl"
            }
            models = {}
            for name, path in model_paths.items():
                try:
                    model = joblib.load(f"model/{path}")
                    models[name] = model
                except Exception as e:
                    st.warning(f"Model {name} not found at {path}: {e}")
            return models
        except Exception as e:
            st.error(f"Error loading models: {e}")
            return {}
    models = load_models()
    # Ensure default value exists in options
    default_models = ["LightGBM"] if "LightGBM" in models else []
    selected_models = st.multiselect("🧠 Choose Models", list(models.keys()), default=default_models)

if not selected_models:
    st.warning("⚠️ Please select at least one model to continue.")
    st.stop()

# <!-- DESIGN: Data Loading and Processing -->
@st.cache_data
def load_historical_data():
    try:
        df = pd.read_csv("data/bgd-rainfall-adm2-full.csv")
        if "ADM2_EN" not in df.columns:
            gdf = gpd.read_file("data/adm2Shape/bgd_admbnda_adm2_bbs_20201113.shp")
            df = df.merge(gdf[['ADM2_PCODE', 'ADM2_EN']], on='ADM2_PCODE', how='left')
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df['month'] = df['date'].dt.month
        df['rfh'] = pd.to_numeric(df['rfh'], errors='coerce')
        df = df.dropna(subset=['date', 'rfh', 'month'])
        return df
    except Exception as e:
        st.error(f"Error loading historical data: {e}")
        return pd.DataFrame()

def generate_recursive_features(historical_data, district, future_dates, model_features, model_name, model):
    try:
        last_values = historical_data[historical_data['ADM2_EN'] == district][['date', 'rfh', 'month']].sort_values('date').tail(6).copy()
        if last_values.empty:
            st.error(f"No historical data found for district {district}")
            return pd.DataFrame()
        forecast_values = []
        month_avg_rfh = historical_data[historical_data['ADM2_EN'] == district].groupby('month')['rfh'].mean()
        max_rainfall = month_avg_rfh.max()
        month_weight = (month_avg_rfh / max_rainfall).to_dict() if not month_avg_rfh.empty else {}
        alpha = 0.7
        base_noise_std = 2.5 if model_name == "XGBoost" else 2.0

        for date in future_dates:
            year = date.year
            month = date.month
            quarter = (month - 1) // 3 + 1
            is_monsoon = 1 if month in [6, 7, 8, 9] else 0

            rfh_lag1 = last_values.iloc[-1]['rfh'] if not last_values.empty else 0
            rfh_lag2 = last_values.iloc[-2]['rfh'] if len(last_values) > 1 else 0
            rfh_roll3 = last_values['rfh'].tail(3).mean() if len(last_values) >= 3 else rfh_lag1
            rfh_roll6 = last_values['rfh'].tail(6).mean() if len(last_values) >= 6 else rfh_roll3
            rfh_diff = rfh_lag1 - rfh_lag2 if len(last_values) > 1 else 0

            month_avg_val = month_avg_rfh.get(month, 0)
            month_w = month_weight.get(month, 1.0)

            row = {
                'year': year,
                'month': month,
                'quarter': quarter,
                'is_monsoon': is_monsoon,
                'rfh_lag1': rfh_lag1,
                'rfh_lag2': rfh_lag2,
                'rfh_roll3': rfh_roll3,
                'rfh_roll6': rfh_roll6,
                'rfh_diff': rfh_diff,
                'sin_month': np.sin(2 * np.pi * month / 12),
                'cos_month': np.cos(2 * np.pi * month / 12),
                'month_avg_rfh': month_avg_val,
                'season_Monsoon': 1 if month in [6, 7, 8, 9] else 0,
                'season_Post-Monsoon': 1 if month in [10, 11] else 0,
                'season_Summer': 1 if month in [3, 4, 5] else 0,
                'season_Winter': 1 if month in [12, 1, 2] else 0,
                'time_idx': (year - 2025) * 12 + month
            }

            input_df = pd.DataFrame([row])
            for col in model_features:
                if col not in input_df.columns:
                    input_df[col] = 0

            input_df = input_df[model_features]
            pred = model.predict(input_df)[0]

            noise = np.random.normal(0, base_noise_std)
            year_var = 1 + np.random.uniform(-0.7, 0.7) if model_name == "XGBoost" else 1 + np.random.uniform(-0.5, 0.5)

            pred = pred * year_var + noise
            pred = (1 - alpha) * pred + alpha * month_avg_val * (month_w ** 1.5)

            forecast_values.append({'date': date, 'yhat': pred})

            new_row = pd.DataFrame({'date': [date], 'rfh': [pred], 'month': [month]})
            last_values = pd.concat([last_values, new_row], ignore_index=True)
            last_values = last_values.iloc[-6:]

        return pd.DataFrame(forecast_values)
    except Exception as e:
        st.error(f"Error in generating recursive features for {model_name}: {e}")
        return pd.DataFrame()

# <!-- DESIGN: Data Processing and Forecast Generation -->
historical_data = load_historical_data()
forecast_df = pd.DataFrame()
for name in selected_models:
    model = models[name]
    try:
        future_dates = pd.date_range(start="2025-01-01", end="2035-12-01", freq="MS")
        model_features = model.feature_names_in_ if hasattr(model, 'feature_names_in_') else [
            'year', 'month', 'quarter', 'is_monsoon', 'rfh_lag1', 'rfh_lag2', 'rfh_roll3', 'rfh_roll6',
            'rfh_diff', 'sin_month', 'cos_month', 'month_avg_rfh', 'season_Monsoon', 'season_Post-Monsoon',
            'season_Summer', 'season_Winter', 'time_idx'
        ]
        forecast_data = generate_recursive_features(historical_data, district, future_dates, model_features, name, model)
        if not forecast_data.empty and 'yhat' in forecast_data.columns:
            forecast_df[name] = forecast_data['yhat']
        else:
            st.error(f"No 'yhat' column in forecast data for {name}")
        forecast_df['Date'] = future_dates
    except Exception as e:
        st.error(f"{name} prediction failed: {e}")

# <!-- DESIGN: Plotting Section -->
if not forecast_df.empty:
    melted_df = forecast_df.melt(id_vars='Date', value_vars=selected_models, var_name='Model', value_name='Rainfall')
    fig = px.line(
        melted_df, x='Date', y='Rainfall', color='Model',
        title=f"Forecasted Rainfall in {district} (2025–2035)",
        color_discrete_sequence=["#3498db", "#2ecc71", "#e74c3c"]
    )
    fig.update_layout(width=900, height=500, template="plotly_white")

    st.markdown('<div class="plot-container">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # <!-- DESIGN: Download Button -->
    st.download_button("📥 Download Forecast CSV", forecast_df.to_csv(index=False), file_name=f"forecast_{district}_2025_2035.csv")

# <!-- DESIGN: Footer Section -->
st.markdown('<div class="footer">Powered by xAI | Rainfall Forecast Dashboard | © 2025</div>', unsafe_allow_html=True)