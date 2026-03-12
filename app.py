import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px

# ----------------------------------
# Title
# ----------------------------------
st.set_page_config(layout="wide")
st.title("🌾 Crop Health Monitoring Dashboard")

# ----------------------------------
# File Paths
# ----------------------------------
csv_file = r"E:\CHM Data 2026\Feb 2026\Crop Health Model\District_Crop_Health_Index.csv"
shp_file = r"E:\CHM Data 2026\Feb 2026\Crop Health Model\IND_SHP\INDIA_DIST_OLDRJ1.shp"

# ----------------------------------
# Load Data
# ----------------------------------
crop_data = pd.read_csv(csv_file)
district_map = gpd.read_file(shp_file)

# ----------------------------------
# Standardize District Names
# ----------------------------------
crop_data['District'] = crop_data['District'].str.upper()
district_map['dtname'] = district_map['dtname'].str.upper()

# ----------------------------------
# Merge Spatial + Crop Data
# ----------------------------------
merged = district_map.merge(
    crop_data,
    left_on='dtname',
    right_on='District',
    how='left'
)

# ----------------------------------
# Handle Missing Values
# ----------------------------------
merged['Crop_Health_Index'] = merged['Crop_Health_Index'].fillna(0)

# ----------------------------------
# Create Centroids for Mapping
# ----------------------------------
merged["lat"] = merged.geometry.centroid.y
merged["lon"] = merged.geometry.centroid.x

# ----------------------------------
# Dashboard Metrics
# ----------------------------------
col1, col2, col3 = st.columns(3)

col1.metric("Average CHI", round(merged["Crop_Health_Index"].mean(), 3))
col2.metric("Total Districts", merged["District"].nunique())
col3.metric("Healthy Districts", (merged["Crop_Health_Index"] > 0.6).sum())

# ----------------------------------
# Crop Health Map
# ----------------------------------
st.subheader("🗺 Crop Health Map")

fig_map = px.scatter_mapbox(
    merged,
    lat="lat",
    lon="lon",
    size="Crop_Health_Index",
    color="Crop_Health_Class",
    hover_name="District",
    zoom=4,
    height=600,
    mapbox_style="carto-positron",
    color_discrete_sequence=px.colors.qualitative.Set1
)

st.plotly_chart(fig_map, use_container_width=True)

# ----------------------------------
# District Table
# ----------------------------------
st.subheader("📊 District Crop Health Data")

st.dataframe(
    merged[
        [
            "State",
            "District",
            "Rainfall",
            "Temperature",
            "NDVI",
            "Crop_Health_Index",
            "Crop_Health_Class"
        ]
    ],
    use_container_width=True
)