import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import os
import numpy as np

def plot_variable_smooth(file_name, var_name, title, output_name, cmap='viridis'):
    if not os.path.exists(file_name):
        print(f"File {file_name} not found. Skipping plot.")
        return
    print(f"Generating smooth plot for {var_name}...")
    ds = xr.open_dataset(file_name)
    
    # Calculate time and depth average (if depth dimension exists)
    if 'depth' in ds.dims:
        ds_mean = ds[var_name].mean(dim=['time', 'depth'])
    else:
        ds_mean = ds[var_name].mean(dim='time')
    
    # Fix for white coastal gaps: BGC datasets mask shallow coastal waters. 
    # We forward/back fill the data arrays slightly to push the colors up to the vector coastline.
    if var_name in ['ph', 'no3', 'po4']:
        ds_mean = ds_mean.ffill(dim='longitude', limit=5).bfill(dim='longitude', limit=5)
        ds_mean = ds_mean.ffill(dim='latitude', limit=5).bfill(dim='latitude', limit=5)
        
    fig = plt.figure(figsize=(10, 8))
    ax = plt.axes(projection=ccrs.PlateCarree())
    
    lon = ds['longitude'].values if 'longitude' in ds else ds['lon'].values
    lat = ds['latitude'].values if 'latitude' in ds else ds['lat'].values
    
    # Contourf provides mathematical interpolation smoothing between grid pixels
    cf = ax.contourf(lon, lat, ds_mean.values.squeeze(), levels=100, transform=ccrs.PlateCarree(), cmap=cmap, extend='both')
    
    # Draw crisp, high-resolution 10m vector coastlines
    ax.add_feature(cfeature.COASTLINE.with_scale('10m'), linewidth=1.5, edgecolor='black')
    ax.add_feature(cfeature.LAND.with_scale('10m'), facecolor='lightgray', zorder=1)
    
    gl = ax.gridlines(draw_labels=True, linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
    gl.top_labels = False
    gl.right_labels = False
    
    units = {
        'thetao': '°C',
        'so': '1e-3 (PSU)',
        'ph': '',
        'no3': 'mmol/m³',
        'po4': 'mmol/m³'
    }
    unit_str = f" [{units.get(var_name, '')}]" if units.get(var_name, '') else ""
    
    cbar = plt.colorbar(cf, ax=ax, shrink=0.7)
    cbar.set_label(f"{var_name.upper()}{unit_str}", fontsize=12)
    plt.title(f"{title} (5-50m mean)", pad=20)
    
    plt.savefig(output_name, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved plot to {output_name}")

if __name__ == "__main__":
    plot_variable_smooth("copernicus_physics_indian_coast_2010_2024.nc", "thetao", "Average Sea Surface Temperature (SST) - Indian Coast (2010-2024)", "Map_SST.png", "plasma")
    plot_variable_smooth("copernicus_physics_indian_coast_2010_2024.nc", "so", "Average Salinity - Indian Coast (2010-2024)", "Map_Salinity.png", "viridis")
    plot_variable_smooth("copernicus_bgc_indian_coast_2010_2024.nc", "ph", "Average pH - Indian Coast (2010-2024)", "Map_pH.png", "cividis")
    plot_variable_smooth("copernicus_bgc_indian_coast_2010_2024.nc", "no3", "Average Nitrate - Indian Coast (2010-2024)", "Map_Nitrate.png", "magma")
    plot_variable_smooth("copernicus_bgc_indian_coast_2010_2024.nc", "po4", "Average Phosphate - Indian Coast (2010-2024)", "Map_Phosphate.png", "magma")
