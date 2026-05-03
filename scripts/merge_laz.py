import os
import sys
import glob
import laspy
import numpy as np

if len(sys.argv) > 1:
    directory = sys.argv[1]
else:
    print("Usage: python merge_laz.py <path_to_directory>")
    sys.exit(1)

# 1. Find and rename _Convert to Las.laz files
print("1. Renaming files...")
laz_files = glob.glob(os.path.join(directory, "*_Convert to Las.laz"))
for file_path in laz_files:
    dir_name = os.path.dirname(file_path)
    base_name = os.path.basename(file_path)
    new_name = base_name.replace("_Convert to Las", "")
    new_path = os.path.join(dir_name, new_name)
    os.rename(file_path, new_path)
    print(f"Renamed {base_name} to {new_name}")

# Find all renamed laz files
all_laz = glob.glob(os.path.join(directory, "*.laz"))

# Filter out the merged file if it exists
merged_name = os.path.basename(directory) + ".laz"
all_laz = [f for f in all_laz if os.path.basename(f) != merged_name]

# 2. Sort by timestamp
print("\n2. Sorting files by timestamp...")
def extract_timestamp(filepath):
    basename = os.path.basename(filepath)
    try:
        ts_str = basename.split('_')[0]
        return float(ts_str)
    except:
        return float('inf')

sorted_laz = sorted(all_laz, key=extract_timestamp)
for f in sorted_laz:
    print(os.path.basename(f))

# 3 & 4. Assign point_source_id and Merge
print("\n3 & 4. Assigning Point Source ID and Merging...")
output_path = os.path.join(directory, merged_name)

if len(sorted_laz) == 0:
    print("No .laz files found to process.")
else:
    first_file = sorted_laz[0]
    with laspy.open(first_file) as first_las:
        header = first_las.header
        # Compute new offset and scale if needed, but we'll try preserving the first file's header
        
        with laspy.open(output_path, mode="w", header=header) as writer:
            flight_line_id = 1
            for filepath in sorted_laz:
                print(f"Processing Flight Line {flight_line_id}: {os.path.basename(filepath)}")
                with laspy.open(filepath) as f:
                    las_data = f.read()
                    
                    # Update point source ID
                    if hasattr(las_data, 'pt_src_id'):
                        las_data.pt_src_id = np.full(len(las_data.points), flight_line_id, dtype=np.uint16)
                    else:
                        las_data.point_source_id = np.full(len(las_data.points), flight_line_id, dtype=np.uint16)
                    
                    writer.write_points(las_data.points)
                flight_line_id += 1

print(f"\nMerge complete. Output saved to: {output_path}")
