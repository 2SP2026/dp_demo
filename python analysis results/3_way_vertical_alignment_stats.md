# 3-Way Vertical Alignment Analysis

## Datasets Compared
1. **Original**: `individual line classified original.laz`
2. **Strip Aligned**: `individual line classified strip aligned.laz`
3. **Overlap Labeled**: `individual line classified strip aligned overlap labeled.laz`

**Sample Interval:** 50 ft
**Search Radius:** 1.0 ft
**Total Target Samples (Grid):** 682

## Pairwise Comparisons (dZ = Dataset 1 - Dataset 2)

### Original vs Strip_Aligned
- **Samples Used:** 446
- **dZ Average:** -0.0021 ft
- **dZ Median:** -0.0169 ft
- **dZ Std Dev:** 0.1190 ft
- **dZ Min/Max:** -0.6584 / 0.5500 ft
- **RMSEz:** 0.1189 ft
- **95th Percentile Error:** 0.2337 ft
- **NMAD:** 0.0909 ft

### Strip_Aligned vs Overlap_Labeled
- **Samples Used:** 434
- **dZ Average:** -0.0180 ft
- **dZ Median:** 0.0000 ft
- **dZ Std Dev:** 0.0837 ft
- **dZ Min/Max:** -0.5842 / 0.5522 ft
- **RMSEz:** 0.0855 ft
- **95th Percentile Error:** 0.1900 ft
- **NMAD:** 0.0000 ft

### Original vs Overlap_Labeled
- **Samples Used:** 429
- **dZ Average:** -0.0189 ft
- **dZ Median:** -0.0169 ft
- **dZ Std Dev:** 0.1318 ft
- **dZ Min/Max:** -0.7241 / 0.5500 ft
- **RMSEz:** 0.1330 ft
- **95th Percentile Error:** 0.2769 ft
- **NMAD:** 0.0946 ft
