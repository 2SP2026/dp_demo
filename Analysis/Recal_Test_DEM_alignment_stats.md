# 3-Way Vertical Alignment Analysis (DEM Rasters)

## Datasets Compared
1. **M1 Standard**: `M1_Standard_PCM_PPK_batched_DEM.tif`
2. **M2 Stripped**: `M2_Stripped_PCM_PPK_batched_DEM.tif`
3. **M3 Recalibrated**: `M3_LMS_RECAL_Then_Standard_PCM_PPK_batched_DEM.tif`

**Sample Interval:** 20 m
**Total Target Samples (Grid):** 484

## Pairwise Comparisons (dZ = Dataset 1 - Dataset 2)

### M1_Standard vs M2_Stripped
- **Samples Used:** 221
- **dZ Average:** 0.0277 m
- **dZ Median:** 0.0147 m
- **dZ Std Dev:** 0.1556 m
- **dZ Min/Max:** -0.4519 / 1.7532 m
- **RMSEz:** 0.1578 m
- **95th Percentile Error:** 0.2381 m
- **NMAD:** 0.0586 m

### M1_Standard vs M3_Recalibrated
- **Samples Used:** 224
- **dZ Average:** 0.0111 m
- **dZ Median:** 0.0040 m
- **dZ Std Dev:** 0.1016 m
- **dZ Min/Max:** -0.1613 / 1.4523 m
- **RMSEz:** 0.1019 m
- **95th Percentile Error:** 0.0456 m
- **NMAD:** 0.0134 m

### M2_Stripped vs M3_Recalibrated
- **Samples Used:** 221
- **dZ Average:** -0.0167 m
- **dZ Median:** -0.0112 m
- **dZ Std Dev:** 0.1074 m
- **dZ Min/Max:** -0.5608 / 0.5440 m
- **RMSEz:** 0.1085 m
- **95th Percentile Error:** 0.2196 m
- **NMAD:** 0.0552 m
