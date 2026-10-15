"""
Model Intelligence & Spatial Cross-Validation Analytics Component.
"""

import os
import plotly.express as px
import streamlit as st
from app.utils import BASE_DIR, get_feature_importances


def render_analytics_view(model, feature_names, df_cv):
    """Render model evaluation metrics, spatial validation, and feature importance."""
    st.subheader("📊 Model Intelligence & Spatial Cross-Validation")
    st.markdown(
        "Detailed performance evaluation of the machine-learning pipeline. "
        "Because geospatial data suffers from spatial autocorrelation (neighboring cells have similar features), "
        "a **Spatial Block Cross-Validation (GroupKFold)** was utilized to prevent data leakage."
    )

    col_metrics, col_imp = st.columns([1.4, 1.6])

    with col_metrics:
        st.markdown("#### 🏆 Cross-Validation Benchmark")
        st.caption("GroupKFold (Spatial 0.02° blocks) preventing geographic memorization:")

        if not df_cv.empty:
            st.dataframe(
                df_cv.style.highlight_max(
                    subset=["PR-AUC (pooled)", "ROC-AUC", "Top5% F1"],
                    color="rgba(16, 185, 129, 0.25)"
                ),
                use_container_width=True
            )
        else:
            st.info("CV metrics file not found.")

        st.markdown(
            """
            **Key Methodological Insights:**
            - **Class Imbalance:** Only **102 of 4,209 cells (2.4%)** contain existing stations. Therefore, **PR-AUC (Precision-Recall AUC)** is the primary metric rather than raw ROC-AUC.
            - **Spatial Leakage Prevention:** Standard k-fold cross-validation achieves artificially inflated scores because test cells lie adjacent to train cells. Grouping by \(0.02^\circ \times 0.02^\circ\) spatial blocks ensures the model generalizes to unseen geographical sectors.
            - **Winning Architecture:** The **Random Forest** achieved superior pooled PR-AUC (0.227 in balanced sample, 0.197 in full) and Top 5% F1 of 0.300, significantly outperforming linear baselines.
            """
        )

    with col_imp:
        st.markdown("#### 🌲 Random Forest Feature Importances")
        df_imp = get_feature_importances(model, feature_names)
        
        if not df_imp.empty:
            fig_imp = px.bar(
                df_imp.sort_values("importance", ascending=True),
                x="percentage",
                y="label",
                orientation="h",
                text="percentage",
                labels={"percentage": "Relative Importance (%)", "label": "Feature Name"},
                color="percentage",
                color_continuous_scale=["#6ee7b7", "#10b981", "#047857"]
            )
            fig_imp.update_traces(
                texttemplate='%{text:.1f}%',
                textposition='outside',
                hovertemplate='<b>%{y}</b><br>Importance: %{x:.2f}%<extra></extra>'
            )
            fig_imp.update_layout(
                height=380,
                margin=dict(l=10, r=30, t=10, b=20),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                coloraxis_showscale=False,
                xaxis=dict(showgrid=True, gridcolor="rgba(148, 163, 184, 0.15)"),
                yaxis=dict(showgrid=False)
            )
            st.plotly_chart(fig_imp, use_container_width=True)

    # Static reports figure if available
    fig_path = os.path.join(BASE_DIR, "reports", "figures", "pr_and_importance.png")
    if os.path.exists(fig_path):
        st.markdown("---")
        st.markdown("#### 📈 Spatial PR Curves & Evaluation Artifacts")
        st.image(
            fig_path,
            caption="Spatial-CV Precision-Recall curves and Random Forest feature importance generated during model training.",
            use_container_width=True
        )
