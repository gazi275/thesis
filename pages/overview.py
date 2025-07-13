import streamlit as st

# Custom CSS for enhanced design
st.markdown(
    """
    <style>
    body {
        background: linear-gradient(135deg, #e0f7fa 0%, #ffffff 70%) !important;
        background-size: cover !important;
        background-attachment: fixed !important;
        background-position: center !important;
        font-family: 'Segoe UI', 'Arial', sans-serif !important;
    }
    .stApp {
        background: none !important;
    }
    .main {
        background-color: #f0f4f8;
        padding: 25px;
        border-radius: 10px;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
        margin: 20px auto;
        max-width: 900px;
        animation: fadeIn 0.5s ease-in;
    }
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    .title {
        color: #000000 !important;
        font-size: 36px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
        text-shadow: 2px 2px 4px #a9a9a9;
    }
    .section {
        background-color: white;
        padding: 20px;
        border: 2px solid #1e90ff;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
        transition: transform 0.3s ease;
    }
    .section:hover {
        transform: translateY(-5px);
    }
    .highlight {
        color: #000000 !important;
        font-weight: 600;
    }
    .footer {
        text-align: center;
        color: #000000 !important;
        font-size: 12px;
        margin-top: 20px;
        padding-top: 10px;
    }
    .stButton>button {
        background-color: #1e90ff;
        color: #000000 !important;
        border-radius: 5px;
        padding: 5px 15px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #104e8b;
        color: #000000 !important;
        transform: scale(1.05);
    }
    * {
        color: #000000 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Main content
st.markdown('<div class="main">', unsafe_allow_html=True)

st.markdown('<div class="title">📃 Overview</div>', unsafe_allow_html=True)

st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown("""
Welcome to the **Rainfall Forecast Dashboard** for Bangladesh 🇧🇩

This interactive tool allows users, researchers, and policymakers to:

- Explore **historical rainfall trends** across districts
- Understand **seasonal patterns** and yearly totals
- Visualize **spatial maps** of rainfall
- Apply **clustering** for district rainfall similarity
- Forecast **rainfall from 2025–2035** using ML and time series models
- Compare model performance using MAE, RMSE, and R²

### ✅ Included Machine Learning Models:
- **XGBoost**
- **Random Forest**
- **LightGBM**
- **ARIMA** (Auto-Regressive Integrated Moving Average)
- **SARIMA** (Seasonal ARIMA)
- **Prophet** by Facebook
- **LSTM** (Deep Learning based Long Short-Term Memory)

---

### 🎯 Goal
Help farmers, planners, and decision-makers adopt **climate-resilient strategies** through rainfall intelligence.

### 📌 Data Source
- Bangladesh Meteorological Department (BMD)
- Processed to include seasonal, monthly, and lagged features

### 📂 Features Engineered
- Month, Year, Quarter
- Lag rainfall: `rfh_lag1`, `rfh_lag2`
- Rolling means: `rfh_roll3`, `rfh_roll6`
- Rainfall difference: `rfh_diff`
- One-hot encoding of districts and seasons

---

### 🧪 How It Works
All models are pre-trained and used for forecasting. Some models are district-specific (ARIMA/SARIMA), while others are trained globally.

Use the sidebar to navigate through all features!
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Placeholder button (can be replaced with actual functionality)
if st.button("Explore More"):
    st.write("This button is a placeholder. Add your navigation or action here!")

st.markdown('<div class="footer">Powered by xAI | Rainfall Dashboard | © 2025</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)