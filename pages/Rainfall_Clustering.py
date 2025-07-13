import streamlit as st
import pandas as pd
import geopandas as gpd
from sklearn.cluster import KMeans
import plotly.graph_objects as go
import json

# Custom CSS for styling
st.markdown(
    """
    <style>
    .main {
        background-color: #f0f4f8;
        padding: 20px;
        border-radius: 10px;
    }
    .stApp {
        background-color: #e6f0fa;
    }
    .title {
        color: #1e90ff;
        font-size: 36px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
        text-shadow: 2px 2px 4px #a9a9a9;
    }
    .sidebar .sidebar-content {
        background-color: #d1e8ff;
        padding: 10px;
        border-radius: 5px;
    }
    .map-container {
        border: 2px solid #1e90ff;
        border-radius: 10px;
        padding: 10px;
        background-color: white;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .stButton>button {
        background-color: #1e90ff;
        color: white;
        border-radius: 5px;
        padding: 5px 15px;
    }
    .stButton>button:hover {
        background-color: #104e8b;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Sidebar for controls
st.sidebar.title("🌧️ Clustering Options")
n_clusters = st.sidebar.slider("Number of Clusters", min_value=2, max_value=6, value=4, step=1)

# Main title
st.markdown('<div class="title">🌧️ Rainfall Clustering Visualization</div>', unsafe_allow_html=True)

@st.cache_data
def load_cluster_data():
    # Load rainfall data and drop the first row
    df = pd.read_csv("data/bgd-rainfall-adm2-full.csv")
    df = df.iloc[1:].reset_index(drop=True)
    
    # Convert 'rfh' to numeric, log non-numeric values for debugging
    df['rfh'] = pd.to_numeric(df['rfh'], errors='coerce')
    non_numeric = df[df['rfh'].isna()]
    if not non_numeric.empty:
        st.warning(f"Found {len(non_numeric)} rows with non-numeric or missing 'rfh' values:\n{non_numeric.head().to_string()}")
        df['rfh'] = df['rfh'].fillna(0)
    
    # Group by ADM2_PCODE and compute mean rainfall
    district_rainfall = df.groupby('ADM2_PCODE')['rfh'].mean().reset_index()
    
    # Load shapefile
    gdf = gpd.read_file("data/adm2Shape/bgd_admbnda_adm2_bbs_20201113.shp")
    
    # Merge with shapefile
    merged_gdf = gdf.merge(district_rainfall, on='ADM2_PCODE', how='left')
    merged_gdf['rfh'] = merged_gdf['rfh'].fillna(0)
    
    return merged_gdf

# Load data
try:
    merged_gdf = load_cluster_data()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# Perform KMeans clustering
kmeans = KMeans(n_clusters=n_clusters, random_state=42)
merged_gdf['cluster'] = kmeans.fit_predict(merged_gdf[['rfh']])

# Prepare hover text
merged_gdf['hover_text'] = merged_gdf['ADM2_EN'] + '<br>Rainfall: ' + merged_gdf['rfh'].round(2).astype(str) + ' mm<br>Cluster: ' + merged_gdf['cluster'].astype(str)

# Convert datetime columns to string to avoid serialization issues
for col in merged_gdf.select_dtypes(include=['datetime64']).columns:
    merged_gdf[col] = merged_gdf[col].astype(str)

# Convert to GeoJSON
geojson_data = json.loads(merged_gdf.to_json())

# Create choropleth map
fig = go.Figure(go.Choroplethmapbox(
    geojson=geojson_data,
    featureidkey="properties.ADM2_PCODE",
    locations=merged_gdf['ADM2_PCODE'],
    z=merged_gdf['cluster'],
    colorscale="Viridis",
    marker_opacity=0.7,
    marker_line_width=0,
    customdata=merged_gdf['hover_text'],
    hovertemplate="%{customdata}<extra></extra>",
))

# Add marker for highest rainfall district
highest_rainfall_row = merged_gdf.loc[merged_gdf['rfh'].idxmax()]
highest_district = highest_rainfall_row['ADM2_EN']
highest_lat = highest_rainfall_row.geometry.centroid.y
highest_lon = highest_rainfall_row.geometry.centroid.x
highest_rainfall = highest_rainfall_row['rfh']

fig.add_trace(go.Scattermapbox(
    lat=[highest_lat],
    lon=[highest_lon],
    mode="markers+text",
    marker=dict(size=12, color="red"),
    text=[f"🌧️ {highest_district}<br>{highest_rainfall:.2f} mm"],
    textposition="top right",
    textfont=dict(size=12, color="white")
))

# Update layout with enhanced design
fig.update_layout(
    mapbox_style="carto-positron",
    mapbox_zoom=6,
    mapbox_center={"lat": 23.685, "lon": 90.3563},
    title={
        'text': "🌍 KMeans Rainfall Clustering",
        'y': 0.95,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top',
        'font': dict(size=24, color='#1e90ff')
    },
    height=700,
    width=1000,
    margin={"r": 0, "t": 50, "l": 0, "b": 0},
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)"
)

# Display map in a styled container
st.markdown('<div class="map-container">', unsafe_allow_html=True)
st.plotly_chart(fig, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# Add a footer
st.markdown(
    "<p style='text-align: center; color: #666; font-size: 12px;'>Powered by xAI | Rainfall Data Clustering | © 2025</p>",
    unsafe_allow_html=True
)