import os
import laspy
import numpy as np
from scipy.spatial import cKDTree

results_dir = r"C:\TempWork\EchoOne\FromWill20260501\Recal_Test\batchResults"
os.makedirs(results_dir, exist_ok=True)

file_m1 = r"C:\TempWork\EchoOne\FromWill20260501\Recal_Test\M1_Standard_PCM_PPK_batched.laz"
file_m2 = r"C:\TempWork\EchoOne\FromWill20260501\Recal_Test\M2_Stripped_PCM_PPK_batched.laz"
file_m3 = r"C:\TempWork\EchoOne\FromWill20260501\Recal_Test\M3_LMS_RECAL_Then_Standard_PCM_PPK_batched.laz"

files = {
    'M1_Standard': file_m1,
    'M2_Stripped': file_m2,
    'M3_Recalibrated': file_m3
}

def get_ground_points(file_path):
    las = laspy.read(file_path)
    # Filter ground points (classification == 2)
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

# Generate 20-m grid
grid_x = np.arange(minx, maxx, 20.0)
grid_y = np.arange(miny, maxy, 20.0)
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
    dist, idx = tree.query(grid_points, k=1, distance_upper_bound=0.3)
    queries[name] = {'dist': dist, 'idx': idx}

def compute_stats(name1, name2):
    dist1, idx1 = queries[name1]['dist'], queries[name1]['idx']
    dist2, idx2 = queries[name2]['dist'], queries[name2]['idx']
    
    valid1 = dist1 <= 0.3
    valid2 = dist2 <= 0.3
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
    ('M1_Standard', 'M2_Stripped'),
    ('M1_Standard', 'M3_Recalibrated'),
    ('M2_Stripped', 'M3_Recalibrated')
]

md_sections = []
for name1, name2 in pairs:
    stats = compute_stats(name1, name2)
    count_both, dz_avg, dz_median, dz_min, dz_max, dz_std, moe, ci_lower, ci_upper, rmse_z, percentile_95, nmad = stats
    
    section = f"### {name1} vs {name2}\n"
    section += f"- **Samples Used:** {count_both:,}\n"
    section += f"- **dZ Average:** {dz_avg:.4f} m\n"
    section += f"- **dZ Median:** {dz_median:.4f} m\n"
    section += f"- **dZ Std Dev:** {dz_std:.4f} m\n"
    section += f"- **dZ Min/Max:** {dz_min:.4f} / {dz_max:.4f} m\n"
    section += f"- **RMSEz:** {rmse_z:.4f} m\n"
    section += f"- **95th Percentile Error:** {percentile_95:.4f} m\n"
    section += f"- **NMAD:** {nmad:.4f} m\n"
    md_sections.append(section)

md_report = "# 3-Way Vertical Alignment Analysis (LAZ Ground Points)\n\n"
md_report += "## Datasets Compared\n"
md_report += f"1. **M1 Standard**: `M1_Standard_PCM_PPK_batched.laz`\n"
md_report += f"2. **M2 Stripped**: `M2_Stripped_PCM_PPK_batched.laz`\n"
md_report += f"3. **M3 Recalibrated**: `M3_LMS_RECAL_Then_Standard_PCM_PPK_batched.laz`\n\n"
md_report += f"**Sample Interval:** 20 m\n"
md_report += f"**Search Radius:** 0.3 m\n"
md_report += f"**Total Target Samples (Grid):** {total_samples:,}\n\n"
md_report += "## Pairwise Comparisons (dZ = Dataset 1 - Dataset 2)\n\n"
md_report += "\n".join(md_sections)

out_file = os.path.join(results_dir, "vertical_alignment_laz_stats.md")
with open(out_file, "w", encoding="utf-8") as f:
    f.write(md_report)

print(f"LAZ Results written to {out_file}")
