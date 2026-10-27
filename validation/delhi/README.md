# Delhi transfer test

Checks whether the model trained on Pune generalises to another Indian city.

**Question:** does the saved Pune model (`models/ev_suitability_model.joblib`), applied unchanged to Delhi, rank cells that already have an OpenStreetMap charging station above other cells, better than chance?

No Pune file is modified. The Pune model is only loaded, never retrained.

## Method

1. A Delhi AOI polygon (urban area of the National Capital Territory) was drawn in the Google Earth Engine Code Editor.
2. The same 500 m grid and the same GEE feature definitions as Pune were used (`gee_feature_extraction_delhi.js`). Cells that are mostly water were dropped.
3. OpenStreetMap features and the `has_station` label were built exactly as for Pune (distance to main roads, counts of fuel stations, malls and parking within 1 km; station within 500 m of the cell centre), projected to EPSG:32643.
4. The Pune model scored every Delhi cell. Metrics were computed against the Delhi labels (PR-AUC against the positive-rate baseline, ROC-AUC, precision and recall for the top 1, 2, 5 and 10% of cells, and a block-bootstrap interval for PR-AUC).

## Files

| File | Contents |
|---|---|
| `gee_feature_extraction_delhi.js` | GEE script (feature export + AOI export) |
| `delhi_transfer_test.ipynb` | Colab notebook that runs the test |
| `aoi_delhi.geojson` | Delhi study-area polygon |
| `delhi_gee_features.csv` | Raw GEE features per cell |
| `osm/` | OSM extracts used (geometry only) |
| `dataset_delhi_scored.csv` | Delhi cells with features, label and Pune-model `score` |
| `results/` | Metrics tables and figures |

## Results

`<FILL IN from results/transfer_metrics.csv and results/topk_metrics.csv>`

## Limitations

- OpenStreetMap charging-station coverage may differ between cities, so the label is noisy and differently noisy from Pune.
- The metrics are measured against existing stations, not true demand.
- A single-city transfer test shows whether the workflow generalises to one other city, not to all cities.
