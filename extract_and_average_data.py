import os
import glob
import xarray as xr
import pandas as pd
import numpy as np

# Spatial bounds for Indian Coast
LAT_MIN, LAT_MAX = 5.0, 25.0
LON_MIN, LON_MAX = 65.0, 90.0

def process_copernicus(file_name, output_csv_name):
    if not os.path.exists(file_name):
        print(f"File {file_name} not found. Skipping...")
        return
        
    print(f"Processing {file_name}...")
    ds = xr.open_dataset(file_name)
    
    # Resample to quarterly averages ('QS' = Quarter Start)
    print("Resampling to quarterly averages...")
    ds_quarterly = ds.resample(time="QS").mean()
    
    # If the dataset contains a depth dimension, average across it to represent the whole column
    if 'depth' in ds_quarterly.dims:
        print("Averaging across depth layers...")
        ds_quarterly = ds_quarterly.mean(dim='depth')
        
    print("Converting to pandas DataFrame (this may take a moment)...")
    df = ds_quarterly.to_dataframe().reset_index()
    # Drop rows where all variable data is NaN (e.g. land masses)
    variables = list(ds.data_vars.keys())
    df = df.dropna(subset=variables, how='all')
    
    print(f"Saving to {output_csv_name}...")
    df.to_csv(output_csv_name, index=False)
    print("Done.\n")

def parse_orca_date(filename):
    # format: cafe.2012001.hdf -> YYYYDDD (DDD = day of year)
    base = os.path.basename(filename).replace("cafe.", "").replace(".hdf", "")
    return pd.to_datetime(base, format='%Y%j')

def process_orca_npp():
    hdf_dir = "orca_npp_hdf"
    if not os.path.exists(hdf_dir):
        print("ORCA directory not found.")
        return
        
    print("Processing ORCA NPP HDF files...")
    files = sorted(glob.glob(os.path.join(hdf_dir, "*.hdf")))
    
    if not files:
        print("No HDF files found.")
        return
        
    # Global coordinates for 1080x2160 array (from 90 to -90 Lat, -180 to 180 Lon)
    lats = np.linspace(90, -90, 1080, endpoint=False)
    lons = np.linspace(-180, 180, 2160, endpoint=False)
    
    # Find indices for our bounding box
    lat_mask = (lats >= LAT_MIN) & (lats <= LAT_MAX)
    lon_mask = (lons >= LON_MIN) & (lons <= LON_MAX)
    
    lat_subset = lats[lat_mask]
    lon_subset = lons[lon_mask]
    
    all_data = []
    
    for f in files:
        date = parse_orca_date(f)
        try:
            from pyhdf.SD import SD, SDC
            hdf = SD(f, SDC.READ)
            dataset = hdf.select(0) # Assuming the first dataset is NPP
            data = dataset.get()
            
            # subset data
            data_subset = data[lat_mask, :][:, lon_mask]
            
            # create xarray dataarray
            da = xr.DataArray(
                data_subset,
                coords=[lat_subset, lon_subset],
                dims=["latitude", "longitude"],
                name="NPP"
            )
            # Add time dim
            da = da.expand_dims(time=[date])
            all_data.append(da)
        except ImportError:
            # Fallback if pyhdf is not installed
            print("pyhdf is required to read standard HDF4 files. Run: pip install pyhdf")
            return
        except Exception as e:
            print(f"Error reading {f}: {e}")
            
    if not all_data:
        return
        
    # Concatenate along time
    ds_npp = xr.concat(all_data, dim="time")
    
    # Handle fill values (often -9999 or similar in these datasets)
    ds_npp = ds_npp.where(ds_npp > -9000)
    
    print("Resampling NPP to quarterly averages...")
    ds_quarterly = ds_npp.resample(time='QS').mean(dim='time')
    
    df = ds_quarterly.to_dataframe().reset_index()
    df = df.dropna(subset=['NPP'])
    
    out_name = "ORCA_NPP_Quarterly_Indian_Coast.csv"
    print(f"Saving to {out_name}...")
    df.to_csv(out_name, index=False)
    print("Done.\n")


if __name__ == "__main__":
    process_copernicus("copernicus_bgc_indian_coast_2010_2024.nc", "Copernicus_BGC_Quarterly.csv")
    process_copernicus("copernicus_physics_indian_coast_2010_2024.nc", "Copernicus_Physics_Quarterly.csv")
    process_orca_npp()
