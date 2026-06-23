import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import math

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Loading massive datasets into memory...")
df_phys = pd.read_csv("Copernicus_Physics_Quarterly.csv")
df_bgc = pd.read_csv("Copernicus_BGC_Quarterly.csv")
df_npp = pd.read_csv("ORCA_NPP_Quarterly_Indian_Coast.csv")
print("Datasets loaded successfully!")

def get_nearest(df, lat, lon):
    # Find the unique lat/lon pairs
    lats = df['latitude'].unique()
    lons = df['longitude'].unique()
    nearest_lat = lats[np.abs(lats - lat).argmin()]
    nearest_lon = lons[np.abs(lons - lon).argmin()]
    
    # Filter df
    filtered = df[(df['latitude'] == nearest_lat) & (df['longitude'] == nearest_lon)]
    return filtered, nearest_lat, nearest_lon

def safe_val(row, col):
    if row.empty:
        return None
    val = row[col].values[0]
    if pd.isna(val):
        return None
    return float(val)

def safe_mean(df, col):
    val = df[col].mean()
    if pd.isna(val):
        return None
    return float(val)

@app.get("/api/data")
def get_data(lat: float, lon: float):
    # Enforce bounding box for Indian Coast (Data only available here)
    if lat < 4.0 or lat > 26.0 or lon < 64.0 or lon > 91.0:
        raise HTTPException(status_code=400, detail="Data unavailable. The downloaded datasets only cover the Indian coastal region (Lat: 5° to 25°, Lon: 65° to 90°). Please click closer to India.")

    phys_data, p_lat, p_lon = get_nearest(df_phys, lat, lon)
    bgc_data, b_lat, b_lon = get_nearest(df_bgc, lat, lon)
    npp_data, n_lat, n_lon = get_nearest(df_npp, lat, lon)
    
    # Ensure times are aligned, Physics has the full quarter list
    timeseries = []
    times = sorted(phys_data['time'].unique())
    for t in times:
        p_row = phys_data[phys_data['time'] == t]
        b_row = bgc_data[bgc_data['time'] == t]
        n_row = npp_data[npp_data['time'] == t]
        
        timeseries.append({
            'time': str(t)[:10],
            'sst': safe_val(p_row, 'thetao'),
            'salinity': safe_val(p_row, 'so'),
            'ph': safe_val(b_row, 'ph'),
            'nitrate': safe_val(b_row, 'no3'),
            'phosphate': safe_val(b_row, 'po4'),
            'npp': safe_val(n_row, 'NPP')
        })
        
    averages = {
        'sst': safe_mean(phys_data, 'thetao'),
        'salinity': safe_mean(phys_data, 'so'),
        'ph': safe_mean(bgc_data, 'ph'),
        'nitrate': safe_mean(bgc_data, 'no3'),
        'phosphate': safe_mean(bgc_data, 'po4'),
        'npp': safe_mean(npp_data, 'NPP')
    }
    
    return {
        "location": {"lat": p_lat, "lon": p_lon},
        "averages": averages,
        "timeseries": timeseries
    }
