import os
import requests
import tarfile
import gzip
import shutil

# Configuration
YEARS = range(2012, 2025)
BASE_URL = "https://orca.science.oregonstate.edu/data/1x2/monthly/cafe.viirs.r2022/hdf/cafe.v.{}.tar"
DOWNLOAD_DIR = "orca_npp_raw"
EXTRACT_DIR = "orca_npp_hdf"

def download_file(url, filepath):
    if os.path.exists(filepath):
        print(f"File {filepath} already exists. Skipping download.")
        return
    print(f"Downloading {url} to {filepath}...")
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(filepath, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"Downloaded {filepath}")

def extract_tar(tar_path, dest_dir):
    print(f"Extracting {tar_path}...")
    with tarfile.open(tar_path, "r") as tar:
        tar.extractall(path=dest_dir)

def unzip_gz_files(src_dir, dest_dir):
    print(f"Unzipping .gz files from {src_dir} to {dest_dir}...")
    for root, _, files in os.walk(src_dir):
        for file in files:
            if file.endswith(".hdf.gz"):
                gz_path = os.path.join(root, file)
                hdf_filename = file[:-3] # remove .gz
                hdf_path = os.path.join(dest_dir, hdf_filename)
                
                if not os.path.exists(hdf_path):
                    with gzip.open(gz_path, 'rb') as f_in:
                        with open(hdf_path, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    print(f"Extracted {hdf_filename}")

def main():
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    os.makedirs(EXTRACT_DIR, exist_ok=True)

    for year in YEARS:
        url = BASE_URL.format(year)
        tar_filename = f"cafe.v.{year}.tar"
        tar_filepath = os.path.join(DOWNLOAD_DIR, tar_filename)
        
        try:
            download_file(url, tar_filepath)
            extract_tar(tar_filepath, DOWNLOAD_DIR) # extract .hdf.gz to download dir
        except Exception as e:
            print(f"Error processing year {year}: {e}")

    # After downloading and extracting tars, gunzip all files
    unzip_gz_files(DOWNLOAD_DIR, EXTRACT_DIR)
    print("NPP Download and Extraction Complete!")

if __name__ == "__main__":
    main()
