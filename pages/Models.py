import streamlit as st
import pandas as pd
import numpy as np
import joblib
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import plotly.express as px

# Model paths (not visible to UI)
_model_files = {
    "XGBoost": "xgb_model.pkl",
    "Random Forest": "rf_model.pkl",
    "LightGBM": "lgbm_model.pkl",
    "Prophet": "prophet_model.pkl"
}

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

# Title
st.markdown('<div class="title">📈 Model Performance Analyzer</div>', unsafe_allow_html=True)

# Sidebar selections
col1, col2 = st.columns([1, 1])
with col1:
    selected_model = st.selectbox("🧠 Select Model", list(_model_files.keys()))
with col2:
    plot_type = st.radio("📊 Select Plot Type", ["Scatter", "Bar"], horizontal=True)

# Load model test data
def load_test_data_and_align_features(_model, test_data_path="data/test_data.csv"):
    df = pd.read_csv(test_data_path)
    if "rfh" not in df.columns:
        raise ValueError("Test data must contain 'rfh' column")
    y_true = df["rfh"]
    X_test_full = df.drop(columns=["rfh", "date"], errors='ignore')
    try:
        model_features = _model.feature_names_in_
    except AttributeError:
        model_features = X_test_full.columns

    season_columns = ['season_Monsoon', 'season_Post-Monsoon', 'season_Summer', 'season_Winter']
    for col in season_columns:
        if col not in X_test_full.columns:
            X_test_full[col] = 0
    available_features = [f for f in model_features if f in X_test_full.columns]
    X_test = X_test_full[available_features]
    return X_test, y_true

def load_prophet_test_data_and_predict(model, test_data_path="data/prophet_test_data.csv"):
    df = pd.read_csv(test_data_path)
    df['ds'] = pd.to_datetime(df['ds'], errors='coerce')
    df = df.dropna()
    forecast = model.predict(df)
    return df["y"].values, forecast["yhat"].values

@st.cache_resource
def load_model_preds():
    results = {}
    for name, path in _model_files.items():
        try:
            model = joblib.load(f"./model/{path}")
            if name == "Prophet":
                y_true, y_pred = load_prophet_test_data_and_predict(model)
            else:
                X_test, y_true = load_test_data_and_align_features(model)
                y_pred = model.predict(X_test)
            results[name] = (y_true, y_pred)
        except Exception as e:
            st.warning(f"⚠️ Failed to load {name}: {e}")
    return results

# Load predictions
models = load_model_preds()
if selected_model not in models:
    st.error("❌ Model failed to load. Check data or model file.")
    st.stop()

y_true, y_pred = models[selected_model]

# Metrics
mae = mean_absolute_error(y_true, y_pred)
rmse = np.sqrt(mean_squared_error(y_true, y_pred))
r2 = r2_score(y_true, y_pred)
accuracy = 100 - (mae / np.mean(y_true) * 100) if np.mean(y_true) != 0 else 0

st.markdown('<div class="metric-container">', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)
col1.metric("MAE", f"{mae:.2f} mm")
col2.metric("RMSE", f"{rmse:.2f} mm")
col3.metric("R²", f"{r2:.2f}")
col4.metric("Accuracy", f"{accuracy:.2f}%")
st.markdown('</div>', unsafe_allow_html=True)

# Plotting
if plot_type == "Scatter":
    fig1 = px.scatter(
        x=y_true, y=y_pred,
        labels={'x': 'Actual Rainfall (mm)', 'y': 'Predicted Rainfall (mm)'},
        title=f"{selected_model} - Actual vs Predicted",
        trendline="ols", color_discrete_sequence=["#3498db"]
    )
    fig1.add_scatter(x=[min(y_true), max(y_true)], y=[min(y_true), max(y_true)],
                     mode='lines', name='Ideal', line=dict(color='red', dash='dash'))
else:
    fig1 = px.bar(
        x=np.arange(len(y_true)),
        y=[y_true, y_pred],
        labels={'x': 'Index', 'value': 'Rainfall (mm)', 'variable': 'Type'},
        title=f"{selected_model} - Actual vs Predicted (Bar)"
    )

fig1.update_layout(width=700, height=500, template="plotly_white")

fig2 = px.scatter(
    x=y_true, y=(y_true - y_pred),
    labels={'x': 'Actual Rainfall (mm)', 'y': 'Residuals (mm)'},
    title=f"{selected_model} - Residuals Analysis",
    color=(y_true - y_pred), color_continuous_scale="RdBu",
    size=(np.abs(y_true - y_pred)), size_max=15
)
fig2.update_layout(width=700, height=500, template="plotly_white")

# ⬅️ Side-by-side layout with more width
col1, col2 = st.columns([1.2, 1.2])
with col1:
    st.markdown('<div class="plot-container">', unsafe_allow_html=True)
    st.plotly_chart(fig1, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="plot-container">', unsafe_allow_html=True)
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown('<div class="footer">Powered by xAI | Model Analysis Dashboard | © 2025</div>', unsafe_allow_html=True)
