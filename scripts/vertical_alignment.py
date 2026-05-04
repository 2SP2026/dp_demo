import os
import glob
import laspy
import numpy as np
from scipy.spatial import cKDTree
import sys

results_dir = r"C:\TempWork\EchoOne\DP event\python analysis results"
os.makedirs(results_dir, exist_ok=True)

file_orig = r"C:\TempWork\EchoOne\DP event\E1-Investigation-LL20260503\individual line classified original\individual line classified original.laz"
file_aligned = r"C:\TempWork\EchoOne\DP event\E1-Investigation-LL20260503\individual line classified strip aligned\individual line classified strip aligned.laz"
file_overlap = r"C:\TempWork\EchoOne\DP event\E1-Investigation-LL20260503\individual line classified strip aligned overlap labeled\individual line classified strip aligned overlap labeled.laz"

files = {
    'Original': file_orig,
    'Strip_Aligned': file_aligned,
    'Overlap_Labeled': file_overlap
}

# Function to extract ground points
def get_ground_points(file_path):
    las = laspy.read(file_path)
    ground_mask = las.classification == 2
    x = las.x[ground_mask]
    y = las.y[ground_mask]
    z = las.z[ground_mask]
    return np.column_stack((x, y, z))

pts_data = {}
print("Loading and filtering ground points...")
for name, path in files.items():
    pts = get_ground_points(path)
    pts_data[name] = pts
    print(f"{name} Ground Points: {len(pts):,}")

# Determine bounding box
minx = min([pts[:, 0].min() for pts in pts_data.values() if len(pts) > 0])
maxx = max([pts[:, 0].max() for pts in pts_data.values() if len(pts) > 0])
miny = min([pts[:, 1].min() for pts in pts_data.values() if len(pts) > 0])
maxy = max([pts[:, 1].max() for pts in pts_data.values() if len(pts) > 0])

# Generate 50-ft grid
grid_x = np.arange(minx, maxx, 50.0)
grid_y = np.arange(miny, maxy, 50.0)
xv, yv = np.meshgrid(grid_x, grid_y)
grid_points = np.column_stack([xv.ravel(), yv.ravel()])
total_samples = len(grid_points)
print(f"Total samples generated: {total_samples:,}")

# KDTrees
trees = {}
print("Building KDTrees...")
for name, pts in pts_data.items():
    trees[name] = cKDTree(pts[:, :2])

# Query KDTrees
queries = {}
print("Querying KDTrees...")
for name, tree in trees.items():
    dist, idx = tree.query(grid_points, k=1, distance_upper_bound=1.0)
    queries[name] = {'dist': dist, 'idx': idx}

def compute_stats(name1, name2):
    dist1, idx1 = queries[name1]['dist'], queries[name1]['idx']
    dist2, idx2 = queries[name2]['dist'], queries[name2]['idx']
    
    valid1 = dist1 <= 1.0
    valid2 = dist2 <= 1.0
    both_valid = valid1 & valid2
    count_both = int(np.sum(both_valid))
    
    if count_both == 0:
        return count_both, 0,0,0,0,0,0,0,0,0,0,0
        
    z1 = pts_data[name1][idx1[both_valid], 2]
    z2 = pts_data[name2][idx2[both_valid], 2]
    dz = z1 - z2
    
    dz_avg = float(np.mean(dz))
    dz_median = float(np.median(dz))
    dz_max = float(np.max(dz))
    dz_min = float(np.min(dz))
    dz_std = float(np.std(dz, ddof=1)) if count_both > 1 else 0.0
    moe = 1.96 * (dz_std / np.sqrt(count_both)) if count_both > 0 else 0.0
    ci_lower = dz_avg - moe
    ci_upper = dz_avg + moe
    rmse_z = float(np.sqrt(np.mean(dz**2)))
    percentile_95 = float(np.percentile(np.abs(dz), 95))
    nmad = 1.4826 * float(np.median(np.abs(dz - dz_median)))
    
    return count_both, dz_avg, dz_median, dz_min, dz_max, dz_std, moe, ci_lower, ci_upper, rmse_z, percentile_95, nmad

pairs = [
    ('Original', 'Strip_Aligned'),
    ('Strip_Aligned', 'Overlap_Labeled'),
    ('Original', 'Overlap_Labeled')
]

md_sections = []
for name1, name2 in pairs:
    stats = compute_stats(name1, name2)
    count_both, dz_avg, dz_median, dz_min, dz_max, dz_std, moe, ci_lower, ci_upper, rmse_z, percentile_95, nmad = stats
    
    section = f"""### {name1} vs {name2}
- **Samples Used:** {count_both:,}
- **dZ Average:** {dz_avg:.4f} ft
- **dZ Median:** {dz_median:.4f} ft
- **dZ Std Dev:** {dz_std:.4f} ft
- **dZ Min/Max:** {dz_min:.4f} / {dz_max:.4f} ft
- **RMSEz:** {rmse_z:.4f} ft
- **95th Percentile Error:** {percentile_95:.4f} ft
- **NMAD:** {nmad:.4f} ft
"""
    md_sections.append(section)

md_report = "# 3-Way Vertical Alignment Analysis\n\n"
md_report += "## Datasets Compared\n"
md_report += f"1. **Original**: `{os.path.basename(file_orig)}`\n"
md_report += f"2. **Strip Aligned**: `{os.path.basename(file_aligned)}`\n"
md_report += f"3. **Overlap Labeled**: `{os.path.basename(file_overlap)}`\n\n"
md_report += f"**Sample Interval:** 50 ft\n"
md_report += f"**Search Radius:** 1.0 ft\n"
md_report += f"**Total Target Samples (Grid):** {total_samples:,}\n\n"
md_report += "## Pairwise Comparisons (dZ = Dataset 1 - Dataset 2)\n\n"
md_report += "\n".join(md_sections)

out_file = os.path.join(results_dir, "3_way_vertical_alignment_stats.md")
with open(out_file, "w", encoding="utf-8") as f:
    f.write(md_report)

print(f"Results written to {out_file}")
