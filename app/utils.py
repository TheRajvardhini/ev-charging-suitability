"""
Utilities, data loaders, and model inference functions for EV Charging Station
Site Suitability Dashboard (Pune, PCMC and Surroundings).
"""

import os
import json
import warnings
import numpy as np
import pandas as pd
import joblib
import streamlit as st
from scipy.spatial import cKDTree

# Suppress sklearn unpickling version warnings
warnings.filterwarnings("ignore", category=UserWarning)

# Approximate project root directory relative to this file
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Key Pune/PCMC Hotspot Presets for quick evaluation
PUNE_HOTSPOTS = {
    "Hinjewadi Phase 1 (IT & Tech Hub)": {
        "lon": 73.7276, "lat": 18.5928,
        "pop": 23.3, "ntl": 48.6, "built_prob": 0.63, "trees_prob": 0.04,
        "ndvi": 0.24, "elev": 613.0, "slope": 4.1,
        "dist_main_road": 45.0, "n_fuel_1km": 2, "n_mall_1km": 1, "n_parking_1km": 4,
        "description": "Dense tech corridor with high commuter inflow and corporate EV fleets."
    },
    "Baner High Street (Commercial / Lifestyle)": {
        "lon": 73.7800, "lat": 18.5570,
        "pop": 63.3, "ntl": 53.4, "built_prob": 0.66, "trees_prob": 0.04,
        "ndvi": 0.23, "elev": 569.6, "slope": 1.8,
        "dist_main_road": 260.0, "n_fuel_1km": 0, "n_mall_1km": 0, "n_parking_1km": 3,
        "description": "High-income suburban corridor with intense nighttime activity and cafe/retail clusters."
    },
    "Viman Nagar / Phoenix Mall Area": {
        "lon": 73.9180, "lat": 18.5620,
        "pop": 85.0, "ntl": 58.2, "built_prob": 0.68, "trees_prob": 0.03,
        "ndvi": 0.19, "elev": 565.0, "slope": 1.5,
        "dist_main_road": 90.0, "n_fuel_1km": 3, "n_mall_1km": 2, "n_parking_1km": 8,
        "description": "Major airport-adjacent retail and entertainment epicenter with heavy vehicle dwell times."
    },
    "Bhosari MIDC (PCMC Industrial & Logistics)": {
        "lon": 73.8458, "lat": 18.6297,
        "pop": 85.6, "ntl": 39.8, "built_prob": 0.65, "trees_prob": 0.04,
        "ndvi": 0.19, "elev": 588.2, "slope": 2.0,
        "dist_main_road": 378.0, "n_fuel_1km": 3, "n_mall_1km": 0, "n_parking_1km": 2,
        "description": "Manufacturing & light industrial heartland of PCMC with EV commercial freight potential."
    },
    "Kothrud (Dense Residential Hub)": {
        "lon": 73.8100, "lat": 18.5080,
        "pop": 115.0, "ntl": 42.0, "built_prob": 0.69, "trees_prob": 0.05,
        "ndvi": 0.22, "elev": 570.0, "slope": 2.2,
        "dist_main_road": 120.0, "n_fuel_1km": 2, "n_mall_1km": 1, "n_parking_1km": 3,
        "description": "Mature western suburb with high private EV 2W/4W adoption and apartment clusters."
    },
    "Swargate Multimodal Transit Hub": {
        "lon": 73.8580, "lat": 18.5020,
        "pop": 130.0, "ntl": 62.0, "built_prob": 0.72, "trees_prob": 0.02,
        "ndvi": 0.15, "elev": 558.0, "slope": 1.2,
        "dist_main_road": 35.0, "n_fuel_1km": 4, "n_mall_1km": 1, "n_parking_1km": 6,
        "description": "Central junction connecting state transport (MSRTC), PMPML city buses, and Pune Metro."
    },
    "Pimpri Colony / Chinchwad Station": {
        "lon": 73.7842, "lat": 18.6293,
        "pop": 108.0, "ntl": 38.4, "built_prob": 0.68, "trees_prob": 0.04,
        "ndvi": 0.22, "elev": 570.5, "slope": 1.7,
        "dist_main_road": 115.0, "n_fuel_1km": 0, "n_mall_1km": 1, "n_parking_1km": 8,
        "description": "Prime commercial and residential center in PCMC with high parking capacity."
    }
}


@st.cache_resource(show_spinner=False)
def load_model():
    """Load the trained Random Forest model bundle."""
    model_path = os.path.join(BASE_DIR, "models", "ev_suitability_model.joblib")
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found at {model_path}")
    
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        bundle = joblib.load(model_path)
    
    model = bundle["model"]
    features = bundle["features"]
    return model, features


@st.cache_data(show_spinner=False)
def load_scored_dataset():
    """Load the 4,209 scored grid cells with spatial distance to nearest station."""
    csv_path = os.path.join(BASE_DIR, "data", "processed", "dataset_scored.csv")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Scored dataset not found at {csv_path}")
    
    df = pd.read_csv(csv_path)
    
    # Calculate km_to_known if not already calculated
    if "km_to_known" not in df.columns:
        lat0 = df["lat"].mean()
        xy = np.c_[df["lon"] * 111.32 * np.cos(np.radians(lat0)), df["lat"] * 110.57]
        known_xy = xy[df["has_station"] == 1]
        if len(known_xy) > 0:
            tree = cKDTree(known_xy)
            df["km_to_known"] = tree.query(xy)[0]
        else:
            df["km_to_known"] = 0.0
            
    return df


@st.cache_data(show_spinner=False)
def load_candidate_sites():
    """Load curated candidate site datasets."""
    p_sim = os.path.join(BASE_DIR, "data", "processed", "candidates_similar.csv")
    p_und = os.path.join(BASE_DIR, "data", "processed", "candidates_underserved.csv")
    
    df_similar = pd.read_csv(p_sim) if os.path.exists(p_sim) else pd.DataFrame()
    df_underserved = pd.read_csv(p_und) if os.path.exists(p_und) else pd.DataFrame()
    return df_similar, df_underserved


@st.cache_data(show_spinner=False)
def load_cv_metrics():
    """Load Cross-Validation benchmark table."""
    csv_path = os.path.join(BASE_DIR, "reports", "cv_results.csv")
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)
    return pd.DataFrame()


@st.cache_data(show_spinner=False)
def load_aoi_geojson():
    """Load the Area of Interest (AOI) GeoJSON polygon."""
    aoi_path = os.path.join(BASE_DIR, "data", "raw", "aoi.geojson")
    if os.path.exists(aoi_path):
        with open(aoi_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def predict_suitability(features_dict, model, feature_names):
    """
    Predict EV charging suitability score (0-100%) given raw inputs.
    Automatically applies log1p transforms for distance and count features.
    """
    # Create copy to calculate log features
    row = dict(features_dict)
    
    # Derive log features if not already calculated
    if "log_dist_main_road" not in row:
        row["log_dist_main_road"] = np.log1p(float(row.get("dist_main_road", 100.0)))
    if "log_n_fuel_1km" not in row:
        row["log_n_fuel_1km"] = np.log1p(float(row.get("n_fuel_1km", 0.0)))
    if "log_n_mall_1km" not in row:
        row["log_n_mall_1km"] = np.log1p(float(row.get("n_mall_1km", 0.0)))
    if "log_n_parking_1km" not in row:
        row["log_n_parking_1km"] = np.log1p(float(row.get("n_parking_1km", 0.0)))
    
    # Order features precisely as expected by the trained model
    input_data = []
    for f in feature_names:
        input_data.append(float(row.get(f, 0.0)))
    
    df_in = pd.DataFrame([input_data], columns=feature_names)
    prob = float(model.predict_proba(df_in)[0, 1])
    score = round(prob * 100, 2)
    return score, prob


def calculate_nearest_station_km(lon, lat, df_scored):
    """Compute distance in km from any arbitrary (lon, lat) to the closest known station."""
    lat0 = 18.52
    known = df_scored[df_scored["has_station"] == 1]
    if len(known) == 0:
        return 0.0
    
    xy_known = np.c_[known["lon"] * 111.32 * np.cos(np.radians(lat0)), known["lat"] * 110.57]
    point_xy = np.array([[lon * 111.32 * np.cos(np.radians(lat0)), lat * 110.57]])
    
    tree = cKDTree(xy_known)
    dist_km = float(tree.query(point_xy)[0][0])
    return round(dist_km, 2)


def get_feature_importances(model, feature_names):
    """Return sorted feature importances from the Random Forest model."""
    if hasattr(model, "feature_importances_"):
        imps = model.feature_importances_
        feature_labels = {
            "log_n_parking_1km": "Parking Density (1km)",
            "ntl": "Night-time Lights (Economic Activity)",
            "pop": "Population Density",
            "log_dist_main_road": "Proximity to Main Roads",
            "built_prob": "Urban Built-up Surface",
            "elev": "Elevation (Terrain Height)",
            "slope": "Terrain Slope",
            "trees_prob": "Tree Canopy / Greenery",
            "ndvi": "Vegetation Index (NDVI)",
            "log_n_fuel_1km": "Fuel Stations (1km)",
            "log_n_mall_1km": "Shopping Malls (1km)"
        }
        data = [
            {
                "feature": f,
                "label": feature_labels.get(f, f),
                "importance": float(imp),
                "percentage": round(float(imp) * 100, 2)
            }
            for f, imp in sorted(zip(feature_names, imps), key=lambda x: -x[1])
        ]
        return pd.DataFrame(data)
    return pd.DataFrame()
