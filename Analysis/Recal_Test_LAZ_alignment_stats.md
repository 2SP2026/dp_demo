# 3-Way Vertical Alignment Analysis (LAZ Ground Points)

## Datasets Compared
1. **M1 Standard**: `M1_Standard_PCM_PPK_batched.laz`
2. **M2 Stripped**: `M2_Stripped_PCM_PPK_batched.laz`
3. **M3 Recalibrated**: `M3_LMS_RECAL_Then_Standard_PCM_PPK_batched.laz`

**Sample Interval:** 20 m
**Search Radius:** 0.3 m
**Total Target Samples (Grid):** 462

## Pairwise Comparisons (dZ = Dataset 1 - Dataset 2)

### M1_Standard vs M2_Stripped
- **Samples Used:** 136
- **dZ Average:** 0.0214 m
- **dZ Median:** 0.0180 m
- **dZ Std Dev:** 0.0355 m
- **dZ Min/Max:** -0.2100 / 0.1880 m
- **RMSEz:** 0.0413 m
- **95th Percentile Error:** 0.0787 m
- **NMAD:** 0.0163 m

### M1_Standard vs M3_Recalibrated
- **Samples Used:** 141
- **dZ Average:** 0.0064 m
- **dZ Median:** 0.0020 m
- **dZ Std Dev:** 0.0350 m
- **dZ Min/Max:** -0.0960 / 0.3310 m
- **RMSEz:** 0.0355 m
- **95th Percentile Error:** 0.0490 m
- **NMAD:** 0.0119 m

### M2_Stripped vs M3_Recalibrated
- **Samples Used:** 139
- **dZ Average:** -0.0168 m
- **dZ Median:** -0.0180 m
- **dZ Std Dev:** 0.0323 m
- **dZ Min/Max:** -0.1130 / 0.2050 m
- **RMSEz:** 0.0363 m
- **95th Percentile Error:** 0.0731 m
- **NMAD:** 0.0178 m
