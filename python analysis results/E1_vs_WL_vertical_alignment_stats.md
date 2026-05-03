# LiDAR Vertical Alignment Analysis

## Configuration
- **Sample Interval:** 50 ftUS
- **Search Radius:** 1 ftUS
- **Ground Class Filter:** Class 2
- **Reference Cloud (E1):** `E1-DP-LLProc20260428c-Comp-A2WL.laz`
- **Target Cloud (WL):** `WL-DP-LLProc20260429-Comp-A2Base.laz`

## Site Coverage (Bounding Box Union)
- **Total Area:** 16.50 Acres (0.0668 Square Kilometers)

## Sampling Breakdown
**Total Samples Generated:** 322

| Group | Description | Count | Percentage |
|-------|-------------|-------|------------|
| 1 | Valid Z found in BOTH | 230 | 71.43% |
| 2 | Valid Z found ONLY in E1 | 62 | 19.25% |
| 3 | Valid Z found ONLY in WL | 15 | 4.66% |
| 4 | No valid Z found | 15 | 4.66% |

## Alignment Statistics (Group 1: Both Valid)
**Number of valid samples used:** 230

*Note: dZ is calculated as `E1 Elevation - WL Elevation` (in ftUS).*

- **dZ Average:** -0.0358 ftUS
- **dZ Median:** -0.0331 ftUS
- **dZ Minimum:** -0.5925 ftUS
- **dZ Maximum:** 0.2711 ftUS
- **dZ Standard Deviation:** 0.1083 ftUS

### Statistical Confidence & Accuracy Metrics
*(Addressing your question on Margin of Error and Confidence Interval)*

- **Margin of Error (95%):** ±0.0140 ftUS
- **95% Confidence Interval for Mean:** [-0.0498, -0.0218] ftUS
- **RMSEz (Root Mean Square Error):** 0.1138 ftUS
- **Normalized Median Absolute Deviation (NMAD):** 0.0719 ftUS
- **95th Percentile Absolute Error:** 0.2392 ftUS

> **Analysis Thought:** The 95% Confidence Interval of the Mean indicates where the true average vertical bias lies. The RMSEz and the 95th Percentile Error are standard ASPRS (American Society for Photogrammetry and Remote Sensing) metrics to evaluate rigorous alignment precision.
