import os
import rasterio
import numpy as np

results_dir = r"C:\TempWork\EchoOne\FromWill20260501\Recal_Test\batchResults"
os.makedirs(results_dir, exist_ok=True)

file_m1 = r"C:\TempWork\EchoOne\FromWill20260501\Recal_Test\M1_Standard_PCM_PPK_batched_DEM.tif"
file_m2 = r"C:\TempWork\EchoOne\FromWill20260501\Recal_Test\M2_Stripped_PCM_PPK_batched_DEM.tif"
file_m3 = r"C:\TempWork\EchoOne\FromWill20260501\Recal_Test\M3_LMS_RECAL_Then_Standard_PCM_PPK_batched_DEM.tif"

files = {
    'M1_Standard': file_m1,
    'M2_Stripped': file_m2,
    'M3_Recalibrated': file_m3
}

dems_data = {}
print("Loading DEMs to find bounding box...")

minx, miny, maxx, maxy = float('inf'), float('inf'), float('-inf'), float('-inf')

for name, path in files.items():
    with rasterio.open(path) as src:
        bounds = src.bounds
        minx = min(minx, bounds.left)
        miny = min(miny, bounds.bottom)
        maxx = max(maxx, bounds.right)
        maxy = max(maxy, bounds.top)

# Generate 20-m grid
grid_x = np.arange(minx, maxx, 20.0)
grid_y = np.arange(miny, maxy, 20.0)
xv, yv = np.meshgrid(grid_x, grid_y)
grid_points = np.column_stack([xv.ravel(), yv.ravel()])
total_samples = len(grid_points)
print(f"Total samples generated: {total_samples:,}")

def get_dem_z_values(path, xy_points):
    with rasterio.open(path) as src:
        nodata = src.nodata
        samples = list(src.sample(xy_points))
        # src.sample returns an iterator of arrays. We extract the first band.
        z_values = np.array([s[0] for s in samples], dtype=float)
        
        # Mark nodata as NaN
        if nodata is not None:
            z_values[z_values == nodata] = np.nan
            
        # Treat extremely low/high values typical of unmasked nodata as NaN
        z_values[z_values < -10000] = np.nan
        z_values[z_values > 30000] = np.nan
        
        return z_values

z_data = {}
print("Extracting Z values from DEMs...")
for name, path in files.items():
    z_data[name] = get_dem_z_values(path, grid_points)
    valid_count = np.sum(~np.isnan(z_data[name]))
    print(f"{name} Valid Z Samples: {valid_count:,}")

def compute_stats(name1, name2):
    z1 = z_data[name1]
    z2 = z_data[name2]
    
    both_valid = ~np.isnan(z1) & ~np.isnan(z2)
    count_both = int(np.sum(both_valid))
    
    if count_both == 0:
        return count_both, 0,0,0,0,0,0,0,0,0,0,0
        
    dz = z1[both_valid] - z2[both_valid]
    
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

md_report = "# 3-Way Vertical Alignment Analysis (DEM Rasters)\n\n"
md_report += "## Datasets Compared\n"
md_report += f"1. **M1 Standard**: `M1_Standard_PCM_PPK_batched_DEM.tif`\n"
md_report += f"2. **M2 Stripped**: `M2_Stripped_PCM_PPK_batched_DEM.tif`\n"
md_report += f"3. **M3 Recalibrated**: `M3_LMS_RECAL_Then_Standard_PCM_PPK_batched_DEM.tif`\n\n"
md_report += f"**Sample Interval:** 20 m\n"
md_report += f"**Total Target Samples (Grid):** {total_samples:,}\n\n"
md_report += "## Pairwise Comparisons (dZ = Dataset 1 - Dataset 2)\n\n"
md_report += "\n".join(md_sections)

out_file = os.path.join(results_dir, "vertical_alignment_dem_stats.md")
with open(out_file, "w", encoding="utf-8") as f:
    f.write(md_report)

print(f"DEM Results written to {out_file}")
