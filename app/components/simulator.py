"""
Live Location Inspector & What-If Scenario Predictor Component.
Provides real-time model inference and policy/intervention simulation.
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from app.utils import PUNE_HOTSPOTS, predict_suitability, calculate_nearest_station_km


def render_simulator_view(model, feature_names, df_scored):
    """Render the interactive What-If scenario simulation studio."""
    st.subheader("⚡ Live Site Inspector & What-If Scenario Predictor")
    st.markdown(
        "Evaluate any site in Pune/PCMC with the trained **Random Forest** model. "
        "Test policy and urban planning interventions (e.g., adding dedicated parking, improving road access) "
        "to observe the real-time impact on EV charging site suitability."
    )

    # Preset selection or custom
    col_preset, col_info = st.columns([1.5, 2])
    with col_preset:
        preset_options = list(PUNE_HOTSPOTS.keys()) + ["Custom Location (User Input)"]
        selected_preset = st.selectbox(
            "📍 Choose a Location or Preset Hotspot",
            preset_options,
            index=0
        )

    # Base values setup
    if selected_preset in PUNE_HOTSPOTS:
        base_data = PUNE_HOTSPOTS[selected_preset]
        desc = base_data.get("description", "")
        with col_info:
            st.info(f"**Neighborhood Profile:** {desc}")
    else:
        # Default custom baseline (Pune mean values)
        base_data = {
            "lon": 73.8567, "lat": 18.5204,
            "pop": float(df_scored["pop"].median()),
            "ntl": float(df_scored["ntl"].median()),
            "built_prob": float(df_scored["built_prob"].median()),
            "trees_prob": float(df_scored["trees_prob"].median()),
            "ndvi": float(df_scored["ndvi"].median()),
            "elev": float(df_scored["elev"].median()),
            "slope": float(df_scored["slope"].median()),
            "dist_main_road": float(df_scored["dist_main_road"].median()),
            "n_fuel_1km": int(df_scored["n_fuel_1km"].median()),
            "n_mall_1km": int(df_scored["n_mall_1km"].median()),
            "n_parking_1km": int(df_scored["n_parking_1km"].median()),
        }
        with col_info:
            st.info("Custom location initialized with median Pune environmental and infrastructure baselines.")

    # Calculate baseline model score
    base_score, base_prob = predict_suitability(base_data, model, feature_names)
    dist_to_station = calculate_nearest_station_km(base_data["lon"], base_data["lat"], df_scored)

    st.markdown("---")
    st.markdown("### 🎛️ What-If Parameter Simulator")
    st.caption("Adjust environmental and infrastructure variables below to see real-time model re-scoring:")

    sim_col1, sim_col2, sim_col3 = st.columns(3)

    with sim_col1:
        st.markdown("**Infrastructure & Amenities**")
        sim_parking = st.slider(
            "🅿️ Designated Parking (1km radius)",
            min_value=0, max_value=20,
            value=int(base_data["n_parking_1km"]),
            help="Designated parking spaces/lots (Model Importance: 22.3%)"
        )
        sim_dist_road = st.slider(
            "🛣️ Distance to Main Road (meters)",
            min_value=5, max_value=2500,
            value=int(base_data["dist_main_road"]),
            step=10,
            help="Proximity to primary or secondary roads (Model Importance: 9.6%)"
        )
        sim_fuel = st.slider(
            "⛽ Fuel Stations (1km radius)",
            min_value=0, max_value=10,
            value=int(base_data["n_fuel_1km"]),
            help="Existing petrol/diesel pumps (Model Importance: 4.5%)"
        )
        sim_malls = st.slider(
            "🛍️ Shopping Malls (1km radius)",
            min_value=0, max_value=6,
            value=int(base_data["n_mall_1km"]),
            help="Major commercial retail centers (Model Importance: 1.0%)"
        )

    with sim_col2:
        st.markdown("**Economic & Population Density**")
        sim_ntl = st.slider(
            "💡 Night-Time Lights Index (VIIRS)",
            min_value=0.0, max_value=90.0,
            value=float(base_data["ntl"]),
            step=1.0,
            help="Satellite measured nighttime radiance representing commercial & transit activity (Model Importance: 17.4%)"
        )
        sim_pop = st.slider(
            "👥 Population (WorldPop 100m grid)",
            min_value=1.0, max_value=200.0,
            value=float(base_data["pop"]),
            step=1.0,
            help="Estimated local resident count per cell (Model Importance: 12.5%)"
        )
        sim_built = st.slider(
            "🏢 Urban Built Surface Probability",
            min_value=0.05, max_value=0.95,
            value=float(base_data["built_prob"]),
            step=0.05,
            help="Dynamic World satellite land-cover built probability (Model Importance: 8.7%)"
        )

    with sim_col3:
        st.markdown("**Topography & Greenery**")
        sim_elev = st.slider(
            "⛰️ Elevation (meters above sea level)",
            min_value=500.0, max_value=850.0,
            value=float(base_data["elev"]),
            step=5.0,
            help="SRTM digital elevation model (Model Importance: 7.8%)"
        )
        sim_slope = st.slider(
            "📐 Terrain Slope (degrees)",
            min_value=0.0, max_value=25.0,
            value=float(base_data["slope"]),
            step=0.5,
            help="Steepness of terrain (gentler slope preferred for civil construction)"
        )
        sim_trees = st.slider(
            "🌳 Tree Canopy Probability",
            min_value=0.01, max_value=0.40,
            value=float(base_data["trees_prob"]),
            step=0.01,
            help="Dynamic World tree coverage"
        )
        sim_ndvi = st.slider(
            "🌿 Vegetation Index (Sentinel-2 NDVI)",
            min_value=0.05, max_value=0.60,
            value=float(base_data["ndvi"]),
            step=0.02,
            help="Normalized Difference Vegetation Index"
        )

    # Form simulated inputs dict
    simulated_inputs = {
        "pop": sim_pop,
        "ntl": sim_ntl,
        "built_prob": sim_built,
        "trees_prob": sim_trees,
        "ndvi": sim_ndvi,
        "elev": sim_elev,
        "slope": sim_slope,
        "dist_main_road": sim_dist_road,
        "n_fuel_1km": sim_fuel,
        "n_mall_1km": sim_malls,
        "n_parking_1km": sim_parking
    }

    # Predict simulated score
    sim_score, sim_prob = predict_suitability(simulated_inputs, model, feature_names)
    delta_score = sim_score - base_score

    # Visualizing Results
    st.markdown("---")
    st.markdown("### 📊 Prediction & Impact Analysis")

    res_col1, res_col2 = st.columns([1.5, 2])

    with res_col1:
        # Gauge chart of Simulated Score
        gauge_color = "#10b981" if sim_score >= 60 else ("#f59e0b" if sim_score >= 35 else "#ef4444")
        
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=sim_score,
            number={"suffix": "%", "font": {"size": 42, "color": gauge_color}},
            delta={
                "reference": base_score,
                "relative": False,
                "valueformat": "+.1f",
                "increasing": {"color": "#10b981"},
                "decreasing": {"color": "#ef4444"}
            },
            title={"text": f"<b>Suitability Score</b><br><span style='font-size:12px;color:gray'>{selected_preset}</span>", "font": {"size": 16}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#94a3b8"},
                "bar": {"color": gauge_color, "thickness": 0.3},
                "bgcolor": "rgba(0,0,0,0.05)",
                "borderwidth": 1,
                "bordercolor": "#cbd5e1",
                "steps": [
                    {"range": [0, 35], "color": "rgba(239, 68, 68, 0.12)"},
                    {"range": [35, 60], "color": "rgba(245, 158, 11, 0.12)"},
                    {"range": [60, 100], "color": "rgba(16, 185, 129, 0.15)"}
                ],
                "threshold": {
                    "line": {"color": "#0ea5e9", "width": 3},
                    "thickness": 0.8,
                    "value": base_score
                }
            }
        ))
        fig_gauge.update_layout(
            height=280,
            margin=dict(l=25, r=25, t=50, b=25),
            paper_bgcolor="rgba(0,0,0,0)",
            font={"family": "sans-serif"}
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

        # Status Badge & Distance to nearest
        st.markdown(
            f"**Distance to nearest existing EV station:** `{dist_to_station} km`"
        )
        if dist_to_station >= 1.0 and sim_score >= 40:
            st.success("🎯 **Strategic Opportunity:** This location qualifies as an **Underserved High-Potential Hub** (high demand + >= 1 km charging gap)!")
        elif sim_score >= 60:
            st.info("⭐ **Prime Corridor:** Matches high-density EV operational profiles.")
        else:
            st.caption("Lower suitability indicates lower transit density, steeper terrain, or limited commercial clustering.")

    with res_col2:
        # Spider / Radar chart comparing Simulated vs Pune Average
        categories = ["Parking", "Night Lights", "Population", "Road Proximity", "Built Urban", "Fuel Access"]
        
        # Normalize 0 to 100 for radar
        pune_mean_parking = min(100, (df_scored["n_parking_1km"].mean() / 6.0) * 100)
        pune_mean_ntl = min(100, (df_scored["ntl"].mean() / 60.0) * 100)
        pune_mean_pop = min(100, (df_scored["pop"].mean() / 100.0) * 100)
        pune_mean_road = min(100, (1.0 - min(df_scored["dist_main_road"].mean(), 1500) / 1500) * 100)
        pune_mean_built = df_scored["built_prob"].mean() * 100
        pune_mean_fuel = min(100, (df_scored["n_fuel_1km"].mean() / 4.0) * 100)

        sim_norm_parking = min(100, (sim_parking / 6.0) * 100)
        sim_norm_ntl = min(100, (sim_ntl / 60.0) * 100)
        sim_norm_pop = min(100, (sim_pop / 100.0) * 100)
        sim_norm_road = min(100, (1.0 - min(sim_dist_road, 1500) / 1500) * 100)
        sim_norm_built = sim_built * 100
        sim_norm_fuel = min(100, (sim_fuel / 4.0) * 100)

        fig_radar = go.Figure()

        fig_radar.add_trace(go.Scatterpolar(
            r=[pune_mean_parking, pune_mean_ntl, pune_mean_pop, pune_mean_road, pune_mean_built, pune_mean_fuel],
            theta=categories,
            fill='toself',
            name='Pune AOI Average',
            line=dict(color='#94a3b8', dash='dash'),
            fillcolor='rgba(148, 163, 184, 0.15)'
        ))

        fig_radar.add_trace(go.Scatterpolar(
            r=[sim_norm_parking, sim_norm_ntl, sim_norm_pop, sim_norm_road, sim_norm_built, sim_norm_fuel],
            theta=categories,
            fill='toself',
            name='Simulated Location',
            line=dict(color='#10b981', width=2),
            fillcolor='rgba(16, 185, 129, 0.25)'
        ))

        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], showticklabels=False)
            ),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
            height=280,
            margin=dict(l=35, r=35, t=20, b=25),
            paper_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    # Narrative explanation of delta
    if abs(delta_score) > 0.05:
        if delta_score > 0:
            st.markdown(
                f"💡 **Model Insight:** The simulated modifications resulted in a **+{delta_score:.1f}% suitability lift**. "
                f"Because **Parking Density** (22.3% importance) and **Night-time radiance** (17.4% importance) are top drivers, "
                f"expanding dedicated charging-bay parking and commercial co-location significantly elevates deployment viability."
            )
        else:
            st.markdown(
                f"⚠️ **Model Insight:** The simulated modifications resulted in a **{delta_score:.1f}% suitability decrease**, "
                f"primarily driven by increased distance from transit arteries or reduced parking availability."
            )
