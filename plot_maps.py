import xarray as xr
import matplotlib.pyplot as plt
import os

def plot_variable(file_name, var_name, title, output_name, cmap='viridis'):
    if not os.path.exists(file_name):
        print(f"File {file_name} not found. Skipping plot.")
        return
    print(f"Generating plot for {var_name}...")
    ds = xr.open_dataset(file_name)
    
    # Calculate time average for the overall map
    ds_mean = ds[var_name].mean(dim='time')
    
    plt.figure(figsize=(10, 8))
    ds_mean.plot(cmap=cmap)
    plt.title(title)
    plt.tight_layout()
    plt.savefig(output_name, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved plot to {output_name}")

if __name__ == "__main__":
    plot_variable("copernicus_physics_indian_coast_2010_2024.nc", "thetao", "Average Sea Surface Temperature (SST) - Indian Coast (2010-2024)", "Map_SST.png", "plasma")
    plot_variable("copernicus_physics_indian_coast_2010_2024.nc", "so", "Average Salinity - Indian Coast (2010-2024)", "Map_Salinity.png", "viridis")
    plot_variable("copernicus_bgc_indian_coast_2010_2024.nc", "ph", "Average pH - Indian Coast (2010-2024)", "Map_pH.png", "cividis")
    plot_variable("copernicus_bgc_indian_coast_2010_2024.nc", "no3", "Average Nitrate - Indian Coast (2010-2024)", "Map_Nitrate.png", "magma")
    plot_variable("copernicus_bgc_indian_coast_2010_2024.nc", "po4", "Average Phosphate - Indian Coast (2010-2024)", "Map_Phosphate.png", "magma")
