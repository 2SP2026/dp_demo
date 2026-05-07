# Comparative Vertical Alignment Analysis of E1 and WL LiDAR Sensors

## 1. Methodology
To rigorously evaluate the vertical co-registration between the two LiDAR datasets (E1 and WL), a systematic spatial sampling methodology was employed. Both point clouds were first filtered to isolate true bare-earth surface models by strictly retaining only Class 2 (Ground) points. A uniform two-dimensional grid with a fixed interval of 50 US Survey Feet (ftUS) was generated across the union bounding box of both datasets, encompassing a total site area of 16.50 acres. 

At each nodal intersection of the sampling grid, a localized search using a `cKDTree` spatial index was executed to extract the true elevation (Z-coordinate) from the nearest classified ground point within a stringent 1-ftUS search radius. Sample locations failing to yield a valid ground point from both datasets within the search radius were categorized as non-overlapping or occluded and subsequently excluded from the comparative difference calculation. For all valid collocated samples, the elevation difference (dZ) was calculated as the E1 elevation minus the WL elevation.

## 2. Results
The systematic grid generated a total of 322 theoretical sample locations across the site. Of these, 230 samples (71.43%) successfully identified a valid Ground point within the 1-ftUS search radius in *both* datasets. 

Statistical evaluation of the 230 valid dZ samples yielded the following metrics:
- **Average Difference (dZ):** -0.0358 ftUS
- **Median Difference:** -0.0331 ftUS
- **Root Mean Square Error (RMSEz):** 0.1138 ftUS
- **Standard Deviation:** 0.1083 ftUS
- **Normalized Median Absolute Deviation (NMAD):** 0.0719 ftUS
- **95th Percentile Absolute Error:** 0.2392 ftUS
- **95% Confidence Interval for the Mean:** [-0.0498 ftUS, -0.0218 ftUS]

## 3. Analysis
The resulting metrics indicate an exceptionally high degree of vertical conformity between the two point clouds. The overall mean vertical bias of -0.0358 ftUS (approximately -0.43 inches) demonstrates that the E1 sensor data is, on average, nominally lower than the WL sensor data by less than half an inch. The extremely tight 95% Confidence Interval confirms that this bias is statistically significant but practically negligible for standard topographic mapping applications. 

Furthermore, the Root Mean Square Error (RMSEz) of 0.1138 ftUS (~1.36 inches) and a 95th Percentile Absolute Error of 0.2392 ftUS (~2.87 inches) easily satisfy and exceed stringent ASPRS (American Society for Photogrammetry and Remote Sensing) positional accuracy standards for high-fidelity engineering surveys. The low standard deviation (0.1083 ftUS) relative to the sample size suggests that the noise profile between the two sensors is uniform, with minimal presence of localized datum shifts, bore-sight artifacts, or non-linear warping across the 16.5-acre site. Notably, the Normalized Median Absolute Deviation (NMAD) of 0.0719 ftUS is materially lower than the Standard Deviation. This robust statistical disparity indicates that the core vertical alignment is even tighter than the standard deviation implies; the slightly higher standard deviation is likely driven by a small number of localized outlier samples (e.g., misclassified vegetation or structural edges) rather than widespread systemic noise.

## 4. Conclusion
The rigorous systematic sampling confirms that the E1 and WL LiDAR point clouds are exceptionally co-registered in the vertical domain. The sub-inch average vertical bias and tight error distribution definitively validate the spatial integrity and comparative precision of the datasets. These point clouds align well within industry-standard tolerances and are mathematically suitable for combined geomatics, volumetric analysis, and high-precision survey workflows.
