import os
import glob
import laspy
import numpy as np

data_dir = r"C:\TempWork\EchoOne\DP event\data for python"
results_dir = r"C:\TempWork\EchoOne\DP event\python analysis results"
scripts_dir = r"C:\TempWork\EchoOne\DP event\scripts"

os.makedirs(results_dir, exist_ok=True)
os.makedirs(scripts_dir, exist_ok=True)

laz_files = glob.glob(os.path.join(data_dir, "*.laz"))

md_content = "# LiDAR Point Cloud Statistics\n\n"

for file_path in laz_files:
    file_name = os.path.basename(file_path)
    file_size_bytes = os.path.getsize(file_path)
    file_size_mb = file_size_bytes / (1024 * 1024)
    
    print(f"Processing {file_name}...")
    try:
        las = laspy.read(file_path)
    except Exception as e:
        md_content += f"## {file_name}\nError reading file: {e}\n\n"
        continue
        
    point_count = len(las.points)
    
    minx, miny, minz = las.header.mins
    maxx, maxy, maxz = las.header.maxs
    
    full_wkt = "No WKT found"
    for vlr in las.header.vlrs:
        if hasattr(vlr, 'string'):
            val = getattr(vlr, 'string', '')
            if isinstance(val, str) and ("PROJCS" in val or "COMPD_CS" in val or "GEOGCS" in val):
                full_wkt = val
                break
            elif isinstance(val, bytes):
                decoded = val.decode('utf-8', errors='ignore')
                if "PROJCS" in decoded or "COMPD_CS" in decoded:
                    full_wkt = decoded
                    break
                
    unit = "Unknown"
    lower_wkt = full_wkt.lower()
    if "us-ft" in lower_wkt or "us survey foot" in lower_wkt or "survey foot" in lower_wkt or "foot_us" in lower_wkt:
        unit = "US Survey Foot"
    elif "metre" in lower_wkt or "meter" in lower_wkt or 'lengthunit["metre"' in lower_wkt:
        unit = "Meter"
        
    area = (maxx - minx) * (maxy - miny)
    density_native = 0
    density_sq_ft = "N/A"
    density_sq_m = "N/A"
    if area > 0 and point_count > 0:
        density_native = point_count / area
        if unit == "US Survey Foot":
            density_sq_ft = density_native
            density_sq_m = density_native / 0.09290304
        elif unit == "Meter":
            density_sq_m = density_native
            density_sq_ft = density_native * 10.7639104

    classes = las.classification
    unique_classes, class_counts = np.unique(classes, return_counts=True)
    enum_class = [f"Class {c}: {count:,} points" for c, count in zip(unique_classes, class_counts)]
    
    returns = las.return_num
    unique_returns, return_counts = np.unique(returns, return_counts=True)
    enum_return = [f"Return {r}: {count:,} points" for r, count in zip(unique_returns, return_counts)]
    
    md_content += f"## {file_name}\n"
    md_content += f"1. **File Name:** {file_name}\n"
    md_content += f"2. **File Disk Size:** {file_size_mb:.2f} MB\n"
    md_content += f"3. **CRS and Unit:** {unit}\n"
    md_content += f"4. **Spatial Extent:**\n"
    md_content += f"   - MinX: {minx:.3f}, MaxX: {maxx:.3f}\n"
    md_content += f"   - MinY: {miny:.3f}, MaxY: {maxy:.3f}\n"
    md_content += f"   - MinZ: {minz:.3f}, MaxZ: {maxz:.3f}\n"
    md_content += f"5. **Total Number of Points:** {point_count:,}\n"
    
    if isinstance(density_sq_ft, float):
        md_content += f"6. **Point Density:** {density_sq_ft:.2f} pts/sq.ftUS | {density_sq_m:.2f} pts/sq.m\n"
    else:
        md_content += f"6. **Point Density:** Native Unit={density_native:.2f} pts/sq.unit\n"
        
    md_content += f"7. **Number of Points grouped by Classification:**\n"
    for e in enum_class:
        md_content += f"   - {e}\n"
    if not enum_class:
        md_content += "   - No enumeration data available for Classification.\n"
        
    md_content += f"8. **Number of Points grouped by Return Number:**\n"
    for e in enum_return:
        md_content += f"   - {e}\n"
    if not enum_return:
        md_content += "   - No enumeration data available for ReturnNumber.\n"
        
    md_content += f"9. **Full WKT:**\n```wkt\n{full_wkt}\n```\n\n"

output_file = os.path.join(results_dir, "point_cloud_stats.md")
with open(output_file, "w", encoding="utf-8") as f:
    f.write(md_content)
    
print(f"Results written to {output_file}")
