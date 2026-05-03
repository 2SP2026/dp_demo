# Flight Trajectory Above Ground Level (AGL) Comparative Analysis

## 1. Objective
The objective of this analysis is to extract, aggregate, and compare the true Above Ground Level (AGL) altitudes maintained by the drone during the E1 and WL LiDAR sensor flights. By comparing the trajectory altitudes against high-resolution bare-earth models, we can evaluate the flight profiles and operational altitudes for both collections.

## 2. Methodology
To calculate the true AGL for each flight, a programmatic spatial analysis was developed using Python (`laspy` for point cloud manipulation and `rasterio` for geospatial raster sampling). The methodology followed these steps:

1. **Data Identification**: For each sensor flight, two core datasets were identified: 
   - The individual segmented drone flight line trajectories (stored as `.laz` point clouds).
   - The 1-foot resolution bare-earth Digital Elevation Model (DEM, stored as `.tif`) derived from the composite, ground-classified point cloud.
2. **Spatial Alignment**: The affine transform of the DEM was inverted to map the absolute X/Y spatial coordinates of each trajectory point directly to corresponding row/column indices on the raster grid.
3. **Elevation Sampling**: The underlying ground elevation (DEM Z) was sampled for each trajectory coordinate. Points falling outside the mapped DEM footprint (resulting in a 'NoData' value) were filtered out to prevent skewing the dataset.
4. **AGL Calculation**: For every valid point, the precise Above Ground Level was calculated as the difference between the absolute trajectory elevation and the underlying ground elevation (`AGL = Trajectory Z - DEM Z`).
5. **Statistical Aggregation**: The resulting AGL values were pooled across all flight lines for each sensor to calculate global descriptive statistics.

## 3. Results

### E1 Sensor Flight Profile
- **Valid Trajectory Points Evaluated**: 115,509 
- **Average AGL**: 417.49 
- **Median AGL**: 419.15 
- **Minimum AGL**: 393.45 
- **Maximum AGL**: 441.39 
- **Standard Deviation**: 11.87 

### WL Sensor Flight Profile
- **Valid Trajectory Points Evaluated**: 23,244 
- **Average AGL**: 271.86 
- **Median AGL**: 270.98 
- **Minimum AGL**: 256.58 
- **Maximum AGL**: 292.15 
- **Standard Deviation**: 7.71 

## 4. Analysis and Comparison
The analysis reveals two distinct flight profiles for the sensors:
- **Operational Altitude**: The WL sensor was flown significantly lower than the E1 sensor, operating at an average altitude of ~271.86 compared to E1's ~417.49.
- **Flight Stability / Terrain Following**: The WL flight maintained a tighter altitude profile relative to the ground beneath it. The standard deviation of the WL flight was 7.71, compared to the E1 flight's 11.87, indicating fewer vertical fluctuations or a more consistent terrain-following response during the WL data collection.
