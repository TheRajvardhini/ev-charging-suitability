var aoi = ee.Geometry.Rectangle([76.95, 28.45, 77.30, 28.80]);
Map.centerObject(aoi, 10);
Map.addLayer(aoi, {color: 'red'}, 'AOI Delhi');
print('AOI area (km2):', aoi.area().divide(1e6));
 
// ---------- 500 m grid (cell centres), same as Pune ----------
var pts = ee.Image.constant(1).clip(aoi).sample({
  region: aoi, projection: 'EPSG:32643', scale: 500, geometries: true
});
var cells = pts.map(function (f) {
  var c = f.geometry().coordinates();
  return ee.Feature(f.geometry().buffer(250).bounds())
    .set({lon: c.get(0), lat: c.get(1)});
});
print('Number of cells:', cells.size());
 
// ---------- Feature layers (identical to Pune) ----------
var pop = ee.ImageCollection('WorldPop/GP/100m/pop')
  .filter(ee.Filter.eq('country', 'IND'))
  .filter(ee.Filter.eq('year', 2020)).mosaic().rename('pop');
 
var ntl = ee.ImageCollection('NOAA/VIIRS/DNB/MONTHLY_V1/VCMCFG')
  .filterDate('2024-01-01', '2025-01-01').select('avg_rad')
  .median().rename('ntl');
 
// Dynamic World: 'water' is added ONLY so water cells can be dropped later in
// Python. The model does not use water_prob.
var dw = ee.ImageCollection('GOOGLE/DYNAMICWORLD/V1')
  .filterBounds(aoi).filterDate('2024-01-01', '2025-01-01')
  .select(['built', 'trees', 'water']).mean()
  .rename(['built_prob', 'trees_prob', 'water_prob']);
 
var ndvi = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
  .filterBounds(aoi).filterDate('2024-11-01', '2025-03-31')
  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
  .median().normalizedDifference(['B8', 'B4']).rename('ndvi');
 
var dem = ee.Image('USGS/SRTMGL1_003').rename('elev');
var slope = ee.Terrain.slope(dem).rename('slope');
 
var stack = pop.addBands([ntl, dw, ndvi, dem, slope]);
 
// ---------- Aggregate per cell ----------
var table = stack.reduceRegions({
  collection: cells, reducer: ee.Reducer.mean(), scale: 100, tileScale: 4
});
 
// ---------- Exports (two tasks appear in the Tasks tab: run BOTH) ----------
Export.table.toDrive({
  collection: table,
  description: 'delhi_gee_features',
  fileFormat: 'CSV',
  selectors: ['lon', 'lat', 'pop', 'ntl', 'built_prob', 'trees_prob',
              'water_prob', 'ndvi', 'elev', 'slope']
});
 
Export.table.toDrive({
  collection: ee.FeatureCollection([ee.Feature(aoi)]),
  description: 'aoi_delhi',
  fileFormat: 'GeoJSON'
});
 
