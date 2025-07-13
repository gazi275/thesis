import streamlit as st
from PIL import Image
import os

# ===== Page Config =====
st.set_page_config(
    page_title="Rainfall Forecast Dashboard",
    page_icon="☔️",
    layout="wide",
)

# ===== Custom CSS for Navbar, Sidebar, and Background =====
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #e0f7fa 0%, #ffffff 70%);
    background-size: cover;
    background-attachment: fixed;
    background-position: center;
    font-family: 'Segoe UI', 'Arial', sans-serif;
}
.navbar {
    background: linear-gradient(90deg, #003049, #0056b3);
    padding: 1rem 2rem;
    display: flex;
    justify-content: center;
    align-items: center;
    color: white;
    position: sticky;
    top: 0;
    z-index: 1001;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}
.navbar-title {
    font-size: 28px;
    font-weight: bold;
    text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.2);
}
.navbar-links a {
    color: white;
    margin: 0 20px;
    text-decoration: none;
    font-size: 18px;
    font-weight: 600;
    transition: all 0.3s ease;
}
.navbar-links a:hover {
    color: #e0f7fa;
    text-shadow: 0 0 5px #e0f7fa;
    transform: scale(1.1);
}
.sidebar-nav {
    background-color: white !important;
    padding: 2.5rem 1.5rem;
    color: #000000;
    font-family: 'Segoe UI', 'Arial', sans-serif;
    height: 100vh;
    width: 300px;
    position: fixed;
    top: 0;
    left: -300px;
    overflow-y: auto;
    box-shadow: 6px 0 20px rgba(0, 0, 0, 0.2);
    z-index: 1000;
    border-right: 3px solid #e0f7fa;
    transition: left 0.5s ease-in-out;
    border-left: 5px solid #0056b3;
}
.sidebar-nav.active {
    left: 0;
}
.sidebar-title {
    font-size: 36px;
    font-weight: 900;
    margin-bottom: 30px;
    text-align: center;
    border-bottom: 4px solid #0056b3;
    padding-bottom: 15px;
    color: #003049;
    text-shadow: 2px 2px 6px rgba(0, 0, 0, 0.1);
    background: linear-gradient(90deg, #003049, #0056b3);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
}
.sidebar-logo {
    display: block;
    margin: 0 auto 35px auto;
    width: 120px;
    border-radius: 50%;
    border: 4px solid #0056b3;
    box-shadow: 0 0 15px rgba(0, 86, 179, 0.3);
    transition: transform 0.4s ease;
}
.sidebar-logo:hover {
    transform: rotate(15deg) scale(1.15);
}
.sidebar-links a {
    color: #003049;
    display: flex;
    align-items: center;
    padding: 18px 25px;
    text-decoration: none;
    font-size: 24px;
    font-weight: 800;
    border-radius: 12px;
    transition: all 0.5s ease;
    background: linear-gradient(90deg, rgba(224, 247, 250, 0.5), rgba(255, 255, 255, 0.8));
    margin-bottom: 12px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}
.sidebar-links a::before {
    content: "🌧️";
    margin-right: 15px;
    font-size: 20px;
    transition: transform 0.4s ease, color 0.4s ease;
}
.sidebar-links a:hover {
    background: linear-gradient(90deg, #0056b3, #007bff);
    color: #ffffff;
    transform: translateX(20px) scale(1.05);
    box-shadow: 0 4px 15px rgba(0, 86, 179, 0.3);
}
.sidebar-links a:hover::before {
    transform: scale(1.3);
    color: #e0f7fa;
}
.sidebar-links a.active {
    background: linear-gradient(90deg, #007bff, #00c4cc);
    color: #ffffff;
    font-weight: 900;
    box-shadow: 0 4px 15px rgba(0, 123, 255, 0.4);
}
.content {
    margin-left: 0;
    padding: 40px;
    transition: margin-left 0.5s ease;
    text-align: center;
}
.content.with-sidebar {
    margin-left: 320px;
}
.banner-img {
    width: 80%;
    max-width: 1200px;
    border-radius: 15px;
    margin: 20px auto;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ===== Session State for Navigation =====
if 'sidebar_active' not in st.session_state:
    st.session_state.sidebar_active = False

# ===== Navbar Function =====
def render_navbar():
    st.markdown('<div class="navbar">', unsafe_allow_html=True)
    st.markdown('<div class="navbar-title">Rainfall AI Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="navbar-links">', unsafe_allow_html=True)
    st.markdown('<a href="/Home" target="_self">Home</a>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ===== Sidebar Function =====
def render_sidebar():
    st.markdown('<div class="sidebar-nav">', unsafe_allow_html=True)
    st.markdown('<img src="assets/logo.png" alt="Logo" class="sidebar-logo">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">Rainfall AI</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="sidebar-links">
        <a href="/Home" target="_self">Home</a>
        <a href="/Overview" target="_self">Overview</a>
        <a href="/Visualization" target="_self">Visualization</a>
        <a href="/Rainfall_Clustering" target="_self">Rainfall Clustering</a>
        <a href="/Model" target="_self">Model</a>
        <a href="/Forecast" target="_self">Forecast</a>
        <a href="/About_Us" target="_self">About Us</a>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ===== Main Content =====
st.markdown('<div class="content">', unsafe_allow_html=True)

# Determine current page
page = st.query_params.get("page", ["Home"])[0]
st.session_state.page = page

# Render navbar
render_navbar()

# Conditional Sidebar and Content
if page == "Home":
    # Home page content
    banner = Image.open("./assets/banne.jpg") if os.path.exists("./assets/banne.jpg") else Image.new("RGB", (800, 200), "#e0f7fa")
    st.image(banner, use_container_width=True, output_format="JPEG", caption="Rainfall Trends & Forecasting in Bangladesh")
    st.markdown("""
    ### Welcome to the Rainfall Analysis & Forecasting App ☔️
    Navigate using the sidebar (available on other pages) to explore various sections.
    """)
else:
    st.session_state.sidebar_active = True
    st.markdown('<div class="content with-sidebar">', unsafe_allow_html=True)
    render_sidebar()
    # Page-specific content (centered)
    if page == "Overview":
        st.markdown("### Overview ☔️")
        st.write("This section provides an overview of the rainfall forecasting system.")
    elif page == "Visualization":
        st.markdown("### Visualization ☔️")
        st.write("Explore visual representations of rainfall data here.")
    elif page == "Rainfall_Clustering":
        st.markdown("### Rainfall Clustering ☔️")
        st.write("Analyze rainfall clustering patterns in this section.")
    elif page == "Model":
        st.markdown("### Model ☔️")
        st.write("Compare and evaluate different rainfall prediction models here.")
    elif page == "Forecast":
        st.markdown("### Forecast ☔️")
        st.write("View future rainfall predictions in this section.")
    elif page == "About_Us":
        st.markdown("### About Us ☔️")
        st.write("Learn more about the team behind this dashboard.")
    else:
        st.markdown("### Unknown Page ☔️")
        st.write("This page is not recognized. Please use the sidebar to navigate.")

st.markdown('</div>', unsafe_allow_html=True)