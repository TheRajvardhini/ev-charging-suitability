"""
Candidate Sites Explorer & Export Component.
"""

import pandas as pd
import streamlit as st


def render_candidates_view(df_scored, df_similar, df_underserved):
    """Render the ranked candidate sites explorer with filtering and CSV export."""
    st.subheader("🎯 EV Charging Candidate Sites Ranking")
    st.markdown(
        "Explore and prioritize potential candidate sites across Pune and PCMC. "
        "Filter for **Underserved 'Charging Deserts'** to expand geographic equity, or focus on **High-Demand Corridors**."
    )

    tab1, tab2, tab3 = st.tabs([
        "📍 Priority Underserved Sites (≥ 1 km Gap)",
        "⭐ Top Demand Candidate Sites",
        "🔍 Custom Candidate Site Search"
    ])

    # Helper function to format tables nicely
    def format_candidate_table(df_subset):
        df_display = df_subset.copy()
        df_display["Suitability Score"] = (df_display["score"] * 100).map("{:.1f}%".format)
        
        if "km_to_known" in df_display.columns:
            df_display["Dist to Nearest Station"] = df_display["km_to_known"].map("{:.2f} km".format)
        
        df_display["Night Lights (NTL)"] = df_display["ntl"].map("{:.1f}".format)
        df_display["Population"] = df_display["pop"].map("{:.1f}".format)
        df_display["Built Prob"] = df_display["built_prob"].map("{:.2f}".format)
        
        if "dist_main_road" in df_display.columns:
            df_display["Main Road Dist"] = df_display["dist_main_road"].map("{:.0f} m".format)
        if "n_parking_1km" in df_display.columns:
            df_display["Parking (1km)"] = df_display["n_parking_1km"].astype(int)

        cols_to_show = [
            c for c in [
                "Suitability Score", "Dist to Nearest Station",
                "lat", "lon", "Night Lights (NTL)", "Population",
                "Built Prob", "Main Road Dist", "Parking (1km)"
            ] if c in df_display.columns
        ]
        return df_display[cols_to_show].reset_index(drop=True)

    with tab1:
        st.markdown(
            "#### 🚀 Priority Underserved Candidate Sites (Charging Deserts)\n"
            "These locations have high suitability scores but are located **at least 1.0 km away** from any existing station, "
            "making them prime candidates to resolve EV range anxiety and expand coverage into unserved suburban clusters."
        )
        if not df_underserved.empty:
            df_und_fmt = format_candidate_table(df_underserved)
            st.dataframe(df_und_fmt, use_container_width=True)
            
            csv_und = df_underserved.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Underserved Sites (CSV)",
                data=csv_und,
                file_name="pune_ev_underserved_candidates.csv",
                mime="text/csv"
            )
        else:
            st.warning("No underserved candidate sites found in data/processed.")

    with tab2:
        st.markdown(
            "#### ⭐ Top Overall Candidate Sites\n"
            "Ranked strictly by highest predicted suitability probability, representing areas with the highest density of commercial, "
            "night-time lighting, and transit infrastructure."
        )
        if not df_similar.empty:
            df_sim_fmt = format_candidate_table(df_similar)
            st.dataframe(df_sim_fmt, use_container_width=True)

            csv_sim = df_similar.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Top Candidates (CSV)",
                data=csv_sim,
                file_name="pune_ev_top_candidates.csv",
                mime="text/csv"
            )
        else:
            st.warning("No similar candidate sites found in data/processed.")

    with tab3:
        st.markdown("#### 🔍 Filter All 4,107 Unserved Grid Cells in Pune/PCMC")
        
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            f_score = st.slider("Min Suitability Score (%)", 10, 80, 40, step=5)
        with c2:
            f_dist = st.slider("Min Dist to Existing Station (km)", 0.0, 5.0, 1.0, step=0.5)
        with c3:
            f_road = st.slider("Max Dist to Main Road (meters)", 50, 2000, 500, step=50)
        with c4:
            f_ntl = st.slider("Min Night-Time Lights Index", 0.0, 70.0, 25.0, step=5.0)

        unserved_df = df_scored[df_scored["has_station"] == 0].copy()
        
        # Apply filters
        cond = (
            (unserved_df["score"] >= (f_score / 100.0)) &
            (unserved_df["km_to_known"] >= f_dist) &
            (unserved_df["dist_main_road"] <= f_road) &
            (unserved_df["ntl"] >= f_ntl)
        )
        filtered = unserved_df[cond].sort_values("score", ascending=False)

        st.info(f"**Found {len(filtered)} candidate grid cells** matching your custom planning criteria.")
        
        if len(filtered) > 0:
            df_filt_fmt = format_candidate_table(filtered.head(100))
            st.dataframe(df_filt_fmt, use_container_width=True)

            csv_filt = filtered.to_csv(index=False).encode("utf-8")
            st.download_button(
                label=f"📥 Download Filtered Results ({len(filtered)} Sites) (CSV)",
                data=csv_filt,
                file_name="pune_ev_custom_filtered_sites.csv",
                mime="text/csv"
            )
        else:
            st.warning("No grid cells match the selected filter criteria. Try relaxing the score or distance thresholds.")
