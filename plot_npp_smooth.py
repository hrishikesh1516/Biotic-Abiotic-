import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np

def plot_npp_smooth():
    print("Generating smooth plot for NPP...")
    df = pd.read_csv('ORCA_NPP_Quarterly_Indian_Coast.csv')
    df_mean = df.groupby(['latitude', 'longitude'])['NPP'].mean().reset_index()
    pivot_df = df_mean.pivot(index='latitude', columns='longitude', values='NPP')

    # Fix for white coastal gaps: ORCA NPP dataset masks out shallow waters.
    # Extrapolate slightly to push colors up to the coastline
    pivot_df = pivot_df.ffill(axis=1, limit=5).bfill(axis=1, limit=5)
    pivot_df = pivot_df.ffill(axis=0, limit=5).bfill(axis=0, limit=5)

    lon = pivot_df.columns.values
    lat = pivot_df.index.values

    fig = plt.figure(figsize=(10, 8))
    ax = plt.axes(projection=ccrs.PlateCarree())

    # Contourf for mathematically smooth interpolation across grids
    cf = ax.contourf(lon, lat, pivot_df.values, levels=100, transform=ccrs.PlateCarree(), cmap='YlGn', extend='max')

    # Draw crisp, high-resolution 10m vector coastlines over the ocean pixels
    ax.add_feature(cfeature.COASTLINE.with_scale('10m'), linewidth=1.5, edgecolor='black')
    ax.add_feature(cfeature.LAND.with_scale('10m'), facecolor='lightgray', zorder=1)

    gl = ax.gridlines(draw_labels=True, linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
    gl.top_labels = False
    gl.right_labels = False

    cbar = plt.colorbar(cf, ax=ax, shrink=0.7)
    cbar.set_label("NPP [mg C / m² / day]", fontsize=12)
    plt.title("Average Net Primary Production (NPP) - Indian Coast (2010-2024)", pad=20)
    
    plt.savefig('Map_NPP.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved plot to Map_NPP.png")

if __name__ == "__main__":
    plot_npp_smooth()
