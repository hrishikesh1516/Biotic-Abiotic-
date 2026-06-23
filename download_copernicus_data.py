import copernicusmarine
import sys

MIN_LON = 65.0
MAX_LON = 90.0
MIN_LAT = 5.0
MAX_LAT = 25.0
START_DATE = "2010-01-01"
END_DATE = "2024-12-31"

def download_physics():
    print("Downloading Copernicus Physics Data (SST, Salinity)...")
    try:
        copernicusmarine.subset(
            dataset_id="cmems_mod_glo_phy_my_0.083deg_P1M-m",
            variables=["thetao", "so"],
            minimum_longitude=MIN_LON,
            maximum_longitude=MAX_LON,
            minimum_latitude=MIN_LAT,
            maximum_latitude=MAX_LAT,
            start_datetime=START_DATE,
            end_datetime=END_DATE,
            minimum_depth=5.0,
            maximum_depth=50.0, # 5-50m range
            output_filename="copernicus_physics_indian_coast_2010_2024.nc"
        )
    except Exception as e:
        print(f"Error downloading physics data: {e}", file=sys.stderr)

def download_bgc():
    print("Downloading Copernicus BGC Data (pH, Nitrate, Phosphate)...")
    try:
        copernicusmarine.subset(
            dataset_id="cmems_mod_glo_bgc_my_0.25deg_P1M-m",
            variables=["ph", "no3", "po4"],
            minimum_longitude=MIN_LON,
            maximum_longitude=MAX_LON,
            minimum_latitude=MIN_LAT,
            maximum_latitude=MAX_LAT,
            start_datetime=START_DATE,
            end_datetime=END_DATE,
            minimum_depth=5.0,
            maximum_depth=50.0, # 5-50m range
            output_filename="copernicus_bgc_indian_coast_2010_2024.nc"
        )
    except Exception as e:
        print(f"Error downloading bgc data: {e}", file=sys.stderr)

if __name__ == "__main__":
    download_physics()
    download_bgc()
