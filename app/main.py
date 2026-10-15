"""
Streamlit Application: EV Charging Station Site Suitability
Pune City, Pimpri-Chinchwad (PCMC) & Surroundings
"""

import os
import sys
import streamlit as st

# Ensure project root is in python path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.utils import (
    load_model,
    load_scored_dataset,
    load_candidate_sites,
    load_cv_metrics,
    load_aoi_geojson
)
from app.components.map_view import render_map_view
from app.components.simulator import render_simulator_view
from app.components.candidates import render_candidates_view
from app.components.analytics import render_analytics_view

# Page Config
st.set_page_config(
    page_title="EV Charging Suitability | Pune & PCMC",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
css_path = os.path.join(os.path.dirname(__file__), "styles.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def main():
    # Sidebar Branding & Navigation
    with st.sidebar:
        st.markdown("<h2 style='color:#10b981; margin-bottom:0;'>⚡ EV Site Finder</h2>", unsafe_allow_html=True)
        st.caption("Pune, PCMC & Surroundings (1,056 km²)")
        st.markdown("---")

        view_choice = st.radio(
            "Navigation Menu",
            [
                "🗺️ Spatial Suitability Map",
                "⚡ Live Predictor & What-If Studio",
                "🎯 Candidate Sites Ranking",
                "📊 Model Analytics & Validation",
                "ℹ️ Methodology & Data Sources"
            ],
            index=0
        )

        st.markdown("---")
        st.markdown("<p class='sidebar-section-title'>📍 Study Area KPIs</p>", unsafe_allow_html=True)
        
        # High-level Metrics in Sidebar
        st.markdown(
            """
            <div class='metric-container'>
                <div class='metric-title'>Region Area</div>
                <div class='metric-value'>1,057 <span style='font-size:1rem;color:#64748b;'>km²</span></div>
                <div class='metric-sub'>Pune, PCMC & Outer Suburbs</div>
            </div>
            <div class='metric-container'>
                <div class='metric-title'>Grid Resolution</div>
                <div class='metric-value'>4,209 <span style='font-size:1rem;color:#64748b;'>cells</span></div>
                <div class='metric-sub'>500m × 500m spatial cells</div>
            </div>
            <div class='metric-container'>
                <div class='metric-title'>Existing Chargers</div>
                <div class='metric-value'>102 <span style='font-size:1rem;color:#64748b;'>stations</span></div>
                <div class='metric-sub'>2.4% baseline positive rate</div>
            </div>
            <div class='metric-container'>
                <div class='metric-title'>Best Model Score</div>
                <div class='metric-value'>75.9%</div>
                <div class='metric-sub'>Random Forest (GroupKFold)</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("---")
        st.markdown(
            "<small style='color:#64748b;'>AIML Project • GEE + OSM + Random Forest<br>"
            "<a href='https://github.com/TheRajvardhini/ev-charging-suitability' target='_blank' style='color:#10b981;text-decoration:none;'>🔗 GitHub Repository</a></small>",
            unsafe_allow_html=True
        )

    # Main App Header
    st.markdown("<h1 class='ev-header-title'>⚡ EV Charging Station Site Suitability</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p class='ev-header-sub'>Spatial AI/ML Framework for Optimal Charging Station Placement across Pune City, PCMC and Surrounding Corridors</p>",
        unsafe_allow_html=True
    )

    # Load Data with Progress Feedback
    try:
        model, feature_names = load_model()
        df_scored = load_scored_dataset()
        df_similar, df_underserved = load_candidate_sites()
        df_cv = load_cv_metrics()
        aoi_geojson = load_aoi_geojson()
    except Exception as e:
        st.error(f"❌ Error loading datasets or model bundle: {e}")
        st.stop()

    # Route Views
    if view_choice == "🗺️ Spatial Suitability Map":
        render_map_view(df_scored, df_similar, df_underserved, aoi_geojson)

    elif view_choice == "⚡ Live Predictor & What-If Studio":
        render_simulator_view(model, feature_names, df_scored)

    elif view_choice == "🎯 Candidate Sites Ranking":
        render_candidates_view(df_scored, df_similar, df_underserved)

    elif view_choice == "📊 Model Analytics & Validation":
        render_analytics_view(model, feature_names, df_cv)

    elif view_choice == "ℹ️ Methodology & Data Sources":
        render_about_view()


def render_about_view():
    """Render comprehensive documentation of the project, data sources, and ML methodology."""
    st.subheader("ℹ️ Project Architecture & Data Engineering Pipeline")
    
    st.markdown(
        """
        ### 🎯 Problem Statement & Objective
        Rapid EV adoption in India requires strategically placed charging stations. Random or purely intuitive placement 
        leads to either underutilized stations or unserved charging deserts.
        
        This project establishes an **end-to-end spatial machine-learning pipeline** that evaluates every **500m × 500m grid cell**
        in the Pune metropolitan area (\(1,056.71\text{ km}^2\)) and computes an objective **Suitability Score (0% – 100%)**.
        """
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🛰️ Google Earth Engine (GEE) Satellite Layers")
        st.markdown(
            """
            | Layer | Satellite Source | Feature Column | Description |
            |---|---|---|---|
            | **Population** | WorldPop (`GP/100m/pop`) | `pop` | Resident human density per 100m grid |
            | **Night Lights** | VIIRS DNB (`VCMCFG`) | `ntl` | Nocturnal economic & transit radiance |
            | **Land Cover** | Dynamic World (`V1`) | `built_prob` | Probability of artificial urban surface |
            | **Vegetation** | Sentinel-2 SR Harmonized | `ndvi` | Green cover & open land index |
            | **Tree Canopy**| Dynamic World (`V1`) | `trees_prob` | Forest/tree cover proportion |
            | **Elevation**  | SRTM (`SRTMGL1_003`) | `elev` | Meters above sea level |
            | **Terrain**    | SRTM (`SRTMGL1_003`) | `slope` | Surface inclination in degrees |
            """
        )

    with col2:
        st.markdown("#### 🗺️ OpenStreetMap (OSM) Infrastructure Layers")
        st.markdown(
            """
            | Layer | OSM Tag Source | Feature Column | Rationale |
            |---|---|---|---|
            | **Road Network** | `highway=*` (motorway, trunk, primary) | `dist_main_road` | EV chargers must be accessible from arterial corridors |
            | **Parking Facilities** | `amenity=parking` | `n_parking_1km` | Available vehicle dwell bays (**#1 model driver**) |
            | **Fuel Stations** | `amenity=fuel` | `n_fuel_1km` | Existing transit refueling hubs |
            | **Shopping Centers**| `shop=mall` | `n_mall_1km` | Destination charging during retail dwell time |
            | **Ground Truth Label**| `amenity=charging_station` | `has_station` | Target label: 1 if station within 500m of cell centre, else 0 |
            """
        )

    st.markdown("---")
    st.markdown("### 🧠 Machine Learning & Spatial Modeling Strategy")
    st.markdown(
        """
        - **Model Architecture:** `RandomForestClassifier` configured with 300 estimators, balanced subsampling for class imbalance (only 2.4% positive cells), and leaf regularization.
        - **No Spatial Coordinate Memorization:** Longitude and latitude are **strictly excluded** from model training features, forcing the trees to learn transferable physical and infrastructure patterns rather than memorizing geographical coordinates.
        - **Spatial Block Cross-Validation:** Standard random K-Fold suffers from acute geospatial autocorrelation (adjacent cells have almost identical satellite pixels). By dividing the region into \(0.02^\circ \times 0.02^\circ\) spatial blocks and using `StratifiedGroupKFold`, all cells within a spatial block are held out together, ensuring rigorous, realistic out-of-fold generalization.
        """
    )


if __name__ == "__main__":
    main()
