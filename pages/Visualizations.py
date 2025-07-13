# pages/2_Visualizations.py
import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import json

# --- Custom CSS for styling ---
st.markdown(
    """
    <style>
    /* Background and general page style */
    .main {
        background-color: #f0f4f8;
        padding: 20px;
        border-radius: 10px;
    }
    .stApp {
        background-color: #e6f0fa;
        color: #1e1e1e;  /* Dark text for readability */
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    /* Title style */
    .css-1v0mbdj h1 {  /* Targets the main title */
        color: #1e90ff !important;
        text-align: center;
        text-shadow: 2px 2px 4px #a9a9a9;
    }
    /* Map container styling */
    .map-container {
        border: 2px solid #1e90ff;
        border-radius: 10px;
        padding: 15px;
        background-color: white;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    /* Make Selectbox and Slider labels black and bold */
    div.stSelectbox > label,
    div.stSlider > label {
        color: black !important;
        font-weight: bold !important;
    }
    /* Dropdown text color */
    div[role="listbox"] {
        color: #1e1e1e !important;
    }
    /* Button style */
    .stButton>button {
        background-color: #1e90ff;
        color: white;
        border-radius: 5px;
        padding: 6px 16px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #104e8b;
        color: white;
    }
    /* Footer text */
    footer {
        color: #666;
        font-size: 12px;
        text-align: center;
        margin-top: 30px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

@st.cache_data
def load_data():
    data = pd.read_csv("data/bgd-rainfall-adm2-full.csv", low_memory=False)
    gdf = gpd.read_file("data/adm2Shape/bgd_admbnda_adm2_bbs_20201113.shp")

    # Fix date column and remove headers/errors
    data = data.iloc[1:].reset_index(drop=True)
    data['date'] = pd.to_datetime(data['date'], errors='coerce')
    data = data.dropna(subset=['date'])
    data['rfh'] = pd.to_numeric(data['rfh'], errors='coerce').fillna(0)

    # Add derived columns
    data['year'] = data['date'].dt.year
    data['month'] = data['date'].dt.month
    data['season'] = data['month'].map({
        12: "Winter", 1: "Winter", 2: "Winter",
        3: "Summer", 4: "Summer", 5: "Summer",
        6: "Monsoon", 7: "Monsoon", 8: "Monsoon", 9: "Monsoon",
        10: "Post-Monsoon", 11: "Post-Monsoon"
    })
    return data, gdf

data, gdf = load_data()

st.title("\U0001F4CA Rainfall Visualizations")

viz_option = st.selectbox("Choose a visualization", [
    "District-wise Rainfall Map",
    "Seasonal Variation",
    "Yearly Rainfall Trend"
])

if viz_option == "District-wise Rainfall Map":
    year = st.slider("Select Year", int(data['year'].min()), int(data['year'].max()), 2020)
    season_option = st.selectbox("Select Season", ["All", "Winter", "Summer", "Monsoon", "Post-Monsoon"])

    df = data[data['year'] == year]
    if season_option != "All":
        df = df[df['season'] == season_option]

    rainfall_summary = df.groupby('ADM2_PCODE')['rfh'].sum().reset_index()
    merged_gdf = gdf.merge(rainfall_summary, on='ADM2_PCODE', how='left')
    merged_gdf['rfh'] = merged_gdf['rfh'].fillna(0)

    # Convert datetime cols to string for JSON serialization
    for col in merged_gdf.select_dtypes(include=['datetime64']).columns:
        merged_gdf[col] = merged_gdf[col].astype(str)

    fig = go.Figure(go.Choroplethmapbox(
        geojson=json.loads(merged_gdf.to_json()),
        locations=merged_gdf['ADM2_PCODE'],
        z=merged_gdf['rfh'],
        colorscale="Blues",
        marker_opacity=0.7,
        marker_line_width=0,
        customdata=merged_gdf['ADM2_EN'],
        hovertemplate="%{customdata}<br>Rainfall: %{z} mm<extra></extra>",
        featureidkey="properties.ADM2_PCODE"
    ))

    fig.update_layout(
        mapbox_style="carto-positron",
        mapbox_zoom=5.5,
        mapbox_center={"lat": 23.685, "lon": 90.3563},
        margin={"r":0,"t":40,"l":0,"b":0},
        title=f"Rainfall in {season_option} {year} by District"
    )

    st.markdown('<div class="map-container">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif viz_option == "Seasonal Variation":
    seasonal_data = data.groupby(['year', 'season'])['rfh'].mean().reset_index()
    fig = px.line(seasonal_data, x='year', y='rfh', color='season',
                  title='Average Rainfall by Season',
                  labels={'rfh': 'Rainfall (mm)', 'year': 'Year'})
    st.plotly_chart(fig, use_container_width=True)

elif viz_option == "Yearly Rainfall Trend":
    yearly_data = data.groupby('year')['rfh'].sum().reset_index()
    fig = px.line(yearly_data, x='year', y='rfh',
                  title='Total Yearly Rainfall',
                  labels={'rfh': 'Rainfall (mm)', 'year': 'Year'})
    st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown(
    "<footer>Powered by xAI | Rainfall Visualizations | © 2025</footer>",
    unsafe_allow_html=True
)
