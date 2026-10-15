# EV Charging Station Site Suitability: Pune, PCMC and Surroundings

A machine-learning project that scores how suitable different locations in Pune city, Pimpri-Chinchwad (PCMC) and the surrounding suburbs are for a new EV charging station. Features come from Google Earth Engine (satellite/raster layers) and OpenStreetMap (roads and points of interest). A Streamlit app displays the suitability score for a chosen location.

> Status: work in progress. This README is updated as each part of the project is completed.

## Area of Interest (AOI)

- **Region:** Pune city, PCMC and suburbs/surroundings, Maharashtra, India
- **How it was made:** polygon drawn in the Google Earth Engine Code Editor and exported as GeoJSON (`data/raw/aoi.geojson`)
- **CRS:** EPSG:4326 (WGS84)
- **Area:** `1056.71 km²` (computed with `aoi.to_crs(32643).area / 1e6`)
- **Bounding box (west, south, east, north):** `[73.68077827, 18.41202303, 74.02272774, 18.78687324]` (from `aoi.total_bounds`)

## Approach

- **Unit of analysis:** 500 m grid cells covering the AOI.
- **Label (proxy):** a cell is labelled 1 if an existing charging station (OpenStreetMap `amenity=charging_station`) lies within 500 m of its centre, otherwise 0.
- **Model:** baseline Logistic Regression compared with Random Forest, using a spatial block split (GroupKFold) to avoid leakage between neighbouring cells.
- **Output:** predicted probability scaled to a 0-100 suitability score. Cells with a high score but no existing station are candidate sites.

**Limitation:** the label shows where stations currently exist, not true demand. OSM may also miss some stations.

## Planned data sources

| Layer | Source | Feature |
|---|---|---|
| Population | WorldPop (`WorldPop/GP/100m/pop`) via GEE | `pop` |
| Night-time lights | VIIRS (`NOAA/VIIRS/DNB/MONTHLY_V1/VCMCFG`) via GEE | `ntl` |
| Land cover | Dynamic World (`GOOGLE/DYNAMICWORLD/V1`) via GEE | `built_prob`, `trees_prob` |
| Vegetation | Sentinel-2 SR (`COPERNICUS/S2_SR_HARMONIZED`) via GEE | `ndvi` |
| Terrain | SRTM (`USGS/SRTMGL1_003`) via GEE | `elev`, `slope` |
| Charging stations (label) | OpenStreetMap | `has_station` |
| Roads, fuel stations, malls, parking | OpenStreetMap | `dist_main_road`, `n_fuel_1km`, `n_mall_1km`, `n_parking_1km` |

Licences and coverage are confirmed on each GEE catalog page. OpenStreetMap data is © OpenStreetMap contributors, licensed under ODbL.

## Repository structure

```
ev-charging-suitability/
├── data/
│   ├── raw/            gee_features.csv, dataset_raw.csv, aoi.geojson
│   └── processed/      dataset_clean.csv, predictions.csv
├── gee/                gee_feature_extraction.js
├── notebooks/          01_dataset_build.ipynb, 02_model.ipynb
├── models/             ev_suitability_model.joblib
├── app/                Streamlit app (Member 3)
├── reports/
├── requirements.txt
└── README.md
```

## Setup

```bash
git clone https://github.com/TheRajvardhini/ev-charging-suitability.git
cd ev-charging-suitability
pip install -r requirements.txt
```

## Results (Spatial Block GroupKFold Cross-Validation)

| Model | PR-AUC (pooled) | PR-AUC (fold mean) | ROC-AUC | Top 5% Precision | Top 5% Recall | Top 5% F1 |
|---|---|---|---|---|---|---|
| **Logistic Regression (baseline)** | 0.147 | 0.175 | 0.861 | 0.190 | 0.392 | 0.256 |
| **Random Forest (Final Model)** | **0.197** | **0.218** | **0.868** | **0.223** | **0.461** | **0.300** |
| **Gradient Boosting (HGB)** | 0.154 | 0.172 | 0.829 | 0.190 | 0.392 | 0.256 |
| **Random Forest (Balanced 102+102)** | **0.227** | **0.231** | **0.877** | 0.209 | 0.431 | 0.281 |

## How to load the model

```python
import joblib
import pandas as pd

bundle = joblib.load('models/ev_suitability_model.joblib')
model = bundle['model']
features = bundle['features']
print('Model features:', features)

# Predict suitability probability for sample grid cells
df = pd.read_csv('data/processed/dataset_scored.csv')
probabilities = model.predict_proba(df[features])[:, 1]
print('Suitability scores (%):', (probabilities * 100)[:5])
```

## Running the Streamlit Web Application

To launch the interactive dashboard:

```bash
# Direct Streamlit launch
streamlit run app/main.py

# Or via python runner
python run_app.py
```

Features included in the application:
- 🗺️ **Spatial Suitability Map:** Interactive Leaflet/Folium map with layer toggles for 102 existing stations, priority underserved sites (charging deserts), top candidate sites, and 4,209 evaluated grid cells.
- ⚡ **Live Predictor & What-If Studio:** Point-and-click or preset Pune hotspot inspector with real-time parameter simulation (parking, roads, NTL, urban density) and radar comparison.
- 🎯 **Candidate Sites Ranking:** Ranked table of underserved and high-demand candidate sites with custom filtering and CSV export.
- 📊 **Model Analytics:** Spatial cross-validation benchmarks, feature importances, and PR curves.

## Technology stack

Python, Pandas, NumPy, Scikit-learn, GeoPandas, OSMnx, Matplotlib/Seaborn, Google Earth Engine, Streamlit, Folium, Plotly, GitHub.

