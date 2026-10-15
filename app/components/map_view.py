"""
Interactive Map Component displaying Pune & PCMC EV Charging Suitability.
"""

import folium
from folium import plugins
import streamlit as st
from streamlit_folium import st_folium


def render_map_view(df_scored, df_similar, df_underserved, aoi_geojson):
    """Render the main interactive spatial suitability map."""
    st.subheader("🗺️ Spatial Suitability Map: Pune, PCMC & Surroundings")
    st.markdown(
        "Explore 500m grid cells evaluated across Pune and PCMC. "
        "Filter cells by suitability threshold, view existing charging networks, and spot strategic candidate locations."
    )

    # Control filters in expander or columns
    with st.expander("⚙️ Map Display & Filter Controls", expanded=True):
        col1, col2, col3, col4 = st.columns([1.2, 1.2, 1.2, 1.4])
        
        with col1:
            tile_choice = st.selectbox(
                "Base Map Style",
                ["CartoDB Positron (Clean)", "OpenStreetMap (Standard)", "CartoDB Dark Matter (Dark)"],
                index=0
            )
        
        with col2:
            show_existing = st.checkbox("Existing EV Stations (102)", value=True)
            show_underserved = st.checkbox("Priority Underserved Sites", value=True)
            
        with col3:
            show_similar = st.checkbox("High Potential Candidate Sites", value=True)
            show_aoi = st.checkbox("Pune/PCMC AOI Boundary", value=True)
            
        with col4:
            show_grid = st.checkbox("Show Scored Grid Heat Cells", value=False)
            min_score = st.slider(
                "Min Grid Suitability Score",
                min_value=10,
                max_value=80,
                value=35,
                step=5,
                help="Filter background grid cells to highlight only moderate and high potential zones."
            )

    tile_map = {
        "CartoDB Positron (Clean)": "cartodbpositron",
        "OpenStreetMap (Standard)": "openstreetmap",
        "CartoDB Dark Matter (Dark)": "cartodbdark_matter"
    }

    # Center on Pune / PCMC
    center_lat = float(df_scored["lat"].mean())
    center_lon = float(df_scored["lon"].mean())

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=11,
        tiles=tile_map.get(tile_choice, "cartodbpositron"),
        control_scale=True
    )

    # Layer 1: AOI Boundary
    if show_aoi and aoi_geojson:
        folium.GeoJson(
            aoi_geojson,
            name="AOI Boundary",
            style_function=lambda x: {
                "fillColor": "#10b981",
                "color": "#059669",
                "weight": 2,
                "fillOpacity": 0.04,
                "dashArray": "6, 6"
            },
            tooltip="Pune & PCMC Study Area Boundary (1056.7 km²)"
        ).add_to(m)

    # Layer 2: Scored Grid Cells (Filtered)
    if show_grid:
        sub_grid = df_scored[(df_scored["score"] >= (min_score / 100.0)) & (df_scored["has_station"] == 0)]
        grid_group = folium.FeatureGroup(name=f"Grid Cells (Score >= {min_score}%)")
        
        # Limit to 600 cells to keep browser responsive
        if len(sub_grid) > 600:
            sub_grid = sub_grid.nlargest(600, "score")

        for _, r in sub_grid.iterrows():
            score_pct = float(r["score"]) * 100
            # Color gradient: yellow to deep orange/red
            if score_pct >= 60:
                color = "#dc2626"
            elif score_pct >= 45:
                color = "#ea580c"
            else:
                color = "#f59e0b"

            tooltip_html = (
                f"<b>Grid Cell</b><br>"
                f"Suitability Score: <b>{score_pct:.1f}%</b><br>"
                f"Population: {float(r['pop']):.1f} / 100m<br>"
                f"Night Lights (NTL): {float(r['ntl']):.1f}<br>"
                f"Built-up Prob: {float(r['built_prob']):.2f}<br>"
                f"Dist to Main Road: {float(r['dist_main_road']):.0f} m"
            )
            folium.CircleMarker(
                [float(r["lat"]), float(r["lon"])],
                radius=4,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.6,
                weight=1,
                tooltip=tooltip_html
            ).add_to(grid_group)
        grid_group.add_to(m)

    # Layer 3: Existing EV Stations
    if show_existing:
        stations_group = folium.FeatureGroup(name="Existing EV Stations")
        for _, r in df_scored[df_scored["has_station"] == 1].iterrows():
            tooltip_html = (
                f"<div style='font-family: sans-serif; font-size: 12px;'>"
                f"<b style='color: #ef4444;'>Existing EV Charging Station</b><br>"
                f"Coordinates: {float(r['lat']):.4f}, {float(r['lon']):.4f}<br>"
                f"Model Suitability Score: <b>{float(r['score']) * 100:.1f}%</b><br>"
                f"Night Lights: {float(r['ntl']):.1f} | Pop: {float(r['pop']):.1f}"
                f"</div>"
            )
            folium.CircleMarker(
                [float(r["lat"]), float(r["lon"])],
                radius=4,
                color="#ef4444",
                fill=True,
                fill_color="#ef4444",
                fill_opacity=0.85,
                weight=1.5,
                tooltip=tooltip_html
            ).add_to(stations_group)
        stations_group.add_to(m)

    # Layer 4: Top Similar Candidate Sites
    if show_similar and not df_similar.empty:
        similar_group = folium.FeatureGroup(name="High Potential Sites")
        for rank, (_, r) in enumerate(df_similar.iterrows(), 1):
            score_pct = float(r["score"]) * 100
            dist_km = float(r.get("km_to_known", 0.0))
            tooltip_html = (
                f"<div style='font-family: sans-serif; font-size: 12px;'>"
                f"<b style='color: #0284c7;'>High Potential Candidate #{rank}</b><br>"
                f"Suitability Score: <b>{score_pct:.1f}%</b><br>"
                f"Dist to Nearest Station: <b>{dist_km:.2f} km</b><br>"
                f"Night Lights: {float(r['ntl']):.1f} | Pop: {float(r['pop']):.1f}<br>"
                f"Coords: {float(r['lat']):.4f}, {float(r['lon']):.4f}"
                f"</div>"
            )
            folium.CircleMarker(
                [float(r["lat"]), float(r["lon"])],
                radius=8,
                color="#0284c7",
                fill=True,
                fill_color="#38bdf8",
                fill_opacity=0.9,
                weight=2,
                tooltip=tooltip_html
            ).add_to(similar_group)
        similar_group.add_to(m)

    # Layer 5: Priority Underserved Candidate Sites
    if show_underserved and not df_underserved.empty:
        underserved_group = folium.FeatureGroup(name="Priority Underserved Sites")
        for rank, (_, r) in enumerate(df_underserved.iterrows(), 1):
            score_pct = float(r["score"]) * 100
            dist_km = float(r.get("km_to_known", 1.0))
            tooltip_html = (
                f"<div style='font-family: sans-serif; font-size: 12px;'>"
                f"<b style='color: #10b981;'>Priority Underserved Candidate #{rank}</b><br>"
                f"Suitability Score: <b>{score_pct:.1f}%</b><br>"
                f"Distance to Nearest Station: <b>{dist_km:.2f} km</b> (Charging Desert)<br>"
                f"Night Lights: {float(r['ntl']):.1f} | Pop: {float(r['pop']):.1f}<br>"
                f"Coords: {float(r['lat']):.4f}, {float(r['lon']):.4f}"
                f"</div>"
            )
            folium.CircleMarker(
                [float(r["lat"]), float(r["lon"])],
                radius=9,
                color="#059669",
                fill=True,
                fill_color="#10b981",
                fill_opacity=0.95,
                weight=2.5,
                tooltip=tooltip_html
            ).add_to(underserved_group)
        underserved_group.add_to(m)

    # Add Fullscreen toggle
    plugins.Fullscreen(position="topright").add_to(m)

    # Render Folium map in Streamlit
    st_folium(m, width="100%", height=560, returned_objects=[])

    # Map Legend & Guide
    col_leg1, col_leg2, col_leg3, col_leg4 = st.columns(4)
    with col_leg1:
        st.markdown(
            "<span class='badge-tag badge-existing'>● Existing Stations</span><br>"
            "<small style='color: #64748b;'>102 known stations in Pune/PCMC</small>",
            unsafe_allow_html=True
        )
    with col_leg2:
        st.markdown(
            "<span class='badge-tag badge-underserved'>● Priority Underserved</span><br>"
            "<small style='color: #64748b;'>Score &ge; 37%, &ge; 1.0 km from existing (Deserts)</small>",
            unsafe_allow_html=True
        )
    with col_leg3:
        st.markdown(
            "<span class='badge-tag badge-similar'>● High Demand Candidates</span><br>"
            "<small style='color: #64748b;'>Top overall model scores (up to 75.9%)</small>",
            unsafe_allow_html=True
        )
    with col_leg4:
        st.markdown(
            "<span class='badge-tag' style='background: rgba(245,158,11,0.15); color: #d97706; border: 1px solid rgba(245,158,11,0.3);'>● Evaluated Grid</span><br>"
            "<small style='color: #64748b;'>500m cells graded across 1,056 km²</small>",
            unsafe_allow_html=True
        )
