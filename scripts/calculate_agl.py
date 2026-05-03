import os
import glob
import laspy
import rasterio
import numpy as np

def calculate_agl_stats():
    target_dir = r"C:\TempWork\EchoOne\DP event\E1 Vs WL\WL-Individual\Extract AGL"
    dem_path = os.path.join(target_dir, "WL-DP-LLProc20260429-Comp_DEM1ftus.tif")
    traj_pattern = os.path.join(target_dir, "*-traj.laz")

    # Load all traj paths
    traj_files = glob.glob(traj_pattern)

    all_agl = []

    print(f"Loading DEM from {dem_path}...")
    with rasterio.open(dem_path) as src:
        dem_arr = src.read(1)
        transform = src.transform
        nodata = src.nodata
        
        # Invert transform to get row/col from x/y
        inv_transform = ~transform
        
        width = src.width
        height = src.height
        
        for traj_file in traj_files:
            print(f"Processing trajectory: {os.path.basename(traj_file)}")
            try:
                las = laspy.read(traj_file)
                
                x_coords = np.array(las.x)
                y_coords = np.array(las.y)
                z_coords = np.array(las.z)
                
                # Calculate col, row coordinates in the DEM
                cols, rows = inv_transform * (x_coords, y_coords)
                cols = np.floor(cols).astype(int)
                rows = np.floor(rows).astype(int)
                
                # Filter indices to only include those within the DEM bounds
                valid_mask = (cols >= 0) & (cols < width) & (rows >= 0) & (rows < height)
                
                valid_rows = rows[valid_mask]
                valid_cols = cols[valid_mask]
                valid_z = z_coords[valid_mask]
                
                # Sample DEM elevations
                dem_z = dem_arr[valid_rows, valid_cols]
                
                # Filter out 'NoData' values from the DEM
                if nodata is not None:
                    # Depending on DEM data type, we handle potential nan or explicit nodata values
                    if np.isnan(nodata):
                        data_mask = ~np.isnan(dem_z)
                    else:
                        data_mask = (dem_z != nodata)
                        
                    valid_z = valid_z[data_mask]
                    dem_z = dem_z[data_mask]
                    
                # AGL Calculation
                agl = valid_z - dem_z
                all_agl.append(agl)
                
            except Exception as e:
                print(f"Error processing {os.path.basename(traj_file)}: {e}")

    if not all_agl:
        print("No valid AGL calculations could be made.")
    else:
        all_agl = np.concatenate(all_agl)
        
        if len(all_agl) == 0:
            print("No overlapping valid points found between trajectories and DEM.")
            return
            
        print("\n--- AGL Statistics ---")
        print(f"Total valid trajectory points: {len(all_agl)}")
        print(f"Average:   {np.mean(all_agl):.4f}")
        print(f"Median:    {np.median(all_agl):.4f}")
        print(f"Min:       {np.min(all_agl):.4f}")
        print(f"Max:       {np.max(all_agl):.4f}")
        print(f"Std Dev:   {np.std(all_agl):.4f}")

if __name__ == "__main__":
    calculate_agl_stats()
