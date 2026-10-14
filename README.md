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
| Land cover | Dynamic World (`GOOGLE/DYNAMIC_WORLD/V1`) via GEE | `built_prob`, `trees_prob` |
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

## Results

To be filled in after model evaluation (ROC-AUC, PR-AUC, precision, recall, F1 for each model).

## How to load the model

To be added once `models/ev_suitability_model.joblib` is saved.

## Technology stack

Python, Pandas, NumPy, Scikit-learn, GeoPandas, OSMnx, Matplotlib/Seaborn, Google Earth Engine, Streamlit, GitHub.
