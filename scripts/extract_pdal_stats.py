import os
import json
import subprocess
import glob

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
    
    env = os.environ.copy()
    osgeo4w_bin = r"C:\Users\LeoZL\AppData\Local\Programs\OSGeo4W\bin"
    # Prepend OSGeo4W bin to avoid conda DLL hell
    env['PATH'] = f"{osgeo4w_bin};" + env.get('PATH', '')
    # Remove conflicting PROJ vars
    for k in ['PROJ_LIB', 'PROJ_DATA', 'GDAL_DATA']:
        if k in env:
            del env[k]
            
    cmd = ["pdal", "info", file_path, "--all", "--enumerate", "Classification,ReturnNumber"]
    try:
        # Pdal info output can be large, we read the stdout
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, env=env)
        info_data = json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running PDAL on {file_name}: {e.stderr}")
        md_content += f"## {file_name}\nError running PDAL: {e.stderr}\n\n"
        continue
    except Exception as e:
        print(f"Error on {file_name}: {e}")
        md_content += f"## {file_name}\nError parsing output: {e}\n\n"
        continue
        
    stats = info_data.get("stats", {})
    bbox = stats.get("bbox", {}).get("native", {}).get("bbox", {})
    if not bbox:
        # Sometimes it's directly in summary
        bbox = info_data.get("summary", {}).get("bounds", {})
    
    point_count = 0
    stats_enums = stats.get("statistic", [])
    for dim in stats_enums:
        if dim.get("name") == "X":
            point_count = dim.get("count")
            break
            
    if point_count == 0:
        point_count = info_data.get("summary", {}).get("num_points", "Unknown")

    metadata = info_data.get("metadata", {})
    
    # Check common places for WKT in pdal info output
    srs_wkt = metadata.get("srs", {}).get("wkt", "")
    if not srs_wkt:
        # Search nested metadata block
        for key, val in metadata.items():
            if isinstance(val, dict) and "srs" in val:
                srs_wkt = val.get("srs", {}).get("wkt", "")
                if srs_wkt:
                    break
            elif isinstance(val, dict) and "spatialreference" in val:
                srs_wkt = val.get("spatialreference", "")
                if srs_wkt:
                    break
    
    full_wkt = srs_wkt
    
    unit = "Unknown"
    if full_wkt:
        lower_wkt = full_wkt.lower()
        if "us-ft" in lower_wkt or "us survey foot" in lower_wkt or "survey foot" in lower_wkt or "foot_us" in lower_wkt:
            unit = "US Survey Foot"
        elif "metre" in lower_wkt or "meter" in lower_wkt or 'lengthunit["metre"' in lower_wkt:
            unit = "Meter"
        
    minx, maxx = bbox.get("minx", 0), bbox.get("maxx", 0)
    miny, maxy = bbox.get("miny", 0), bbox.get("maxy", 0)
    minz, maxz = bbox.get("minz", 0), bbox.get("maxz", 0)
    
    area = (maxx - minx) * (maxy - miny)
    
    density_native = 0
    density_sq_ft = "N/A"
    density_sq_m = "N/A"
    if area > 0 and isinstance(point_count, int):
        density_native = point_count / area
        if unit == "US Survey Foot":
            density_sq_ft = density_native
            density_sq_m = density_native / 0.09290304
        elif unit == "Meter":
            density_sq_m = density_native
            density_sq_ft = density_native / 10.7639104

    enum_class = []
    enum_return = []
    for dim in stats_enums:
        if dim.get("name") == "Classification":
            counts = dim.get("counts", [])
            for c in counts:
                enum_class.append(f"Class {c.get('value', c.get('val'))}: {c.get('count')} points")
        if dim.get("name") == "ReturnNumber":
            counts = dim.get("counts", [])
            for c in counts:
                enum_return.append(f"Return {c.get('value', c.get('val'))}: {c.get('count')} points")
                
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
