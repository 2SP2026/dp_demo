import os
import glob
import laspy
import numpy as np
from scipy.spatial import cKDTree

data_dir = r"C:\TempWork\EchoOne\DP event\data for python"
results_dir = r"C:\TempWork\EchoOne\DP event\python analysis results"
scripts_dir = r"C:\TempWork\EchoOne\DP event\scripts"

os.makedirs(results_dir, exist_ok=True)
os.makedirs(scripts_dir, exist_ok=True)

# Identify the two files
laz_files = glob.glob(os.path.join(data_dir, "*.laz"))
if len(laz_files) < 2:
    print("Need at least 2 files.")
    exit(1)

# Sort them so E1 and WL are easily identifiable if named properly
e1_file = next((f for f in laz_files if "E1" in os.path.basename(f)), laz_files[0])
wl_file = next((f for f in laz_files if "WL" in os.path.basename(f) and f != e1_file), laz_files[1])

print(f"E1 File: {os.path.basename(e1_file)}")
print(f"WL File: {os.path.basename(wl_file)}")

# Function to extract ground points
def get_ground_points(file_path):
    las = laspy.read(file_path)
    # Filter class 2
    ground_mask = las.classification == 2
    x = las.x[ground_mask]
    y = las.y[ground_mask]
    z = las.z[ground_mask]
    return np.column_stack((x, y, z))

print("Loading and filtering ground points for E1...")
e1_pts = get_ground_points(e1_file)
print(f"E1 Ground Points: {len(e1_pts)}")

print("Loading and filtering ground points for WL...")
wl_pts = get_ground_points(wl_file)
print(f"WL Ground Points: {len(wl_pts)}")

# Determine bounding box
# We will use the union bounding box to cover the entire site
minx = min(e1_pts[:, 0].min(), wl_pts[:, 0].min())
maxx = max(e1_pts[:, 0].max(), wl_pts[:, 0].max())
miny = min(e1_pts[:, 1].min(), wl_pts[:, 1].min())
maxy = max(e1_pts[:, 1].max(), wl_pts[:, 1].max())

area_sq_ft = (maxx - minx) * (maxy - miny)
area_acres = area_sq_ft / 43560.0
area_sq_m = area_sq_ft * 0.09290304
area_sq_km = area_sq_m / 1000000.0

# Generate 50-ft grid
grid_x = np.arange(minx, maxx, 50.0)
grid_y = np.arange(miny, maxy, 50.0)
xv, yv = np.meshgrid(grid_x, grid_y)
grid_points = np.column_stack([xv.ravel(), yv.ravel()])
total_samples = len(grid_points)
print(f"Total samples generated: {total_samples}")

# KDTree for 1-ft search
print("Building KDTrees...")
tree_e1 = cKDTree(e1_pts[:, :2])
tree_wl = cKDTree(wl_pts[:, :2])

print("Querying KDTrees...")
dist_e1, idx_e1 = tree_e1.query(grid_points, k=1, distance_upper_bound=1.0)
dist_wl, idx_wl = tree_wl.query(grid_points, k=1, distance_upper_bound=1.0)

# Valid masks
valid_e1 = dist_e1 <= 1.0
valid_wl = dist_wl <= 1.0

# Groups
both_valid = valid_e1 & valid_wl
only_e1_valid = valid_e1 & (~valid_wl)
only_wl_valid = (~valid_e1) & valid_wl
neither_valid = (~valid_e1) & (~valid_wl)

count_both = int(np.sum(both_valid))
count_only_e1 = int(np.sum(only_e1_valid))
count_only_wl = int(np.sum(only_wl_valid))
count_neither = int(np.sum(neither_valid))

# Extract Z for both valid
z_e1 = e1_pts[idx_e1[both_valid], 2]
z_wl = wl_pts[idx_wl[both_valid], 2]

# dZ calculation (E1 - WL)
dz = z_e1 - z_wl

# Stats
if count_both > 0:
    dz_avg = float(np.mean(dz))
    dz_median = float(np.median(dz))
    dz_max = float(np.max(dz))
    dz_min = float(np.min(dz))
    dz_std = float(np.std(dz, ddof=1))
    
    # Margin of Error & Confidence Interval (95%)
    # MoE = 1.96 * (Std / sqrt(n))
    moe = 1.96 * (dz_std / np.sqrt(count_both))
    ci_lower = dz_avg - moe
    ci_upper = dz_avg + moe
    
    # Additional industry metrics:
    rmse_z = float(np.sqrt(np.mean(dz**2)))
    percentile_95 = float(np.percentile(np.abs(dz), 95))
    nmad = 1.4826 * float(np.median(np.abs(dz - dz_median)))
else:
    dz_avg = dz_median = dz_max = dz_min = dz_std = 0.0
    moe = ci_lower = ci_upper = rmse_z = percentile_95 = nmad = 0.0

# Create Markdown
md = f"""# LiDAR Vertical Alignment Analysis

## Configuration
- **Sample Interval:** 50 ftUS
- **Search Radius:** 1 ftUS
- **Ground Class Filter:** Class 2
- **Reference Cloud (E1):** `{os.path.basename(e1_file)}`
- **Target Cloud (WL):** `{os.path.basename(wl_file)}`

## Site Coverage (Bounding Box Union)
- **Total Area:** {area_acres:,.2f} Acres ({area_sq_km:,.4f} Square Kilometers)

## Sampling Breakdown
**Total Samples Generated:** {total_samples:,}

| Group | Description | Count | Percentage |
|-------|-------------|-------|------------|
| 1 | Valid Z found in BOTH | {count_both:,} | {(count_both/total_samples)*100:.2f}% |
| 2 | Valid Z found ONLY in E1 | {count_only_e1:,} | {(count_only_e1/total_samples)*100:.2f}% |
| 3 | Valid Z found ONLY in WL | {count_only_wl:,} | {(count_only_wl/total_samples)*100:.2f}% |
| 4 | No valid Z found | {count_neither:,} | {(count_neither/total_samples)*100:.2f}% |

## Alignment Statistics (Group 1: Both Valid)
**Number of valid samples used:** {count_both:,}

*Note: dZ is calculated as `E1 Elevation - WL Elevation` (in ftUS).*

- **dZ Average:** {dz_avg:.4f} ftUS
- **dZ Median:** {dz_median:.4f} ftUS
- **dZ Minimum:** {dz_min:.4f} ftUS
- **dZ Maximum:** {dz_max:.4f} ftUS
- **dZ Standard Deviation:** {dz_std:.4f} ftUS

### Statistical Confidence & Accuracy Metrics
*(Addressing your question on Margin of Error and Confidence Interval)*

- **Margin of Error (95%):** ±{moe:.4f} ftUS
- **95% Confidence Interval for Mean:** [{ci_lower:.4f}, {ci_upper:.4f}] ftUS
- **RMSEz (Root Mean Square Error):** {rmse_z:.4f} ftUS
- **Normalized Median Absolute Deviation (NMAD):** {nmad:.4f} ftUS
- **95th Percentile Absolute Error:** {percentile_95:.4f} ftUS

> **Analysis Thought:** The 95% Confidence Interval of the Mean indicates where the true average vertical bias lies. The RMSEz and the 95th Percentile Error are standard ASPRS (American Society for Photogrammetry and Remote Sensing) metrics to evaluate rigorous alignment precision.
"""

out_file = os.path.join(results_dir, "vertical_alignment_stats.md")
with open(out_file, "w", encoding="utf-8") as f:
    f.write(md)
    
print(f"Results written to {out_file}")
