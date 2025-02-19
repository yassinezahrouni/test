import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime
import shutil
import zipfile
import pandas as pd
import json

# Define the GDELT URL and target folder
GDELT_URL = "http://data.gdeltproject.org/events/index.html"
DOWNLOADS_DIR = os.path.expanduser("~/Downloads")  # Default downloads directory
TARGET_DIR = "/Users/yassinezahrouni/coding/test/gdelt"

SELECTED_COLUMNS = ["News Location", "ActionGeo_CountryCode", "ActionGeo_Lat", "ActionGeo_Long", "News Date", "SOURCEURL"]

def get_latest_file_url(base_url):
    """
    Scrape the GDELT page and identify the latest file URL based on the naming convention.
    """
    response = requests.get(base_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    
    files = []
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if href.endswith(".zip"):
            try:
                date_str = href.split(".")[0]
                date_obj = datetime.strptime(date_str, "%Y%m%d")
                files.append((date_obj, urljoin(base_url, href)))
            except ValueError:
                continue

    latest_file = max(files, key=lambda x: x[0])
    return latest_file[1]

def decompress_zip_file(zip_path, extract_to):
    """
    Decompress a zip file.
    """
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print(f"Decompressed {zip_path} to {extract_to}")

def move_file_to_target(download_dir, target_dir, file_name):
    """
    Move a file from the Downloads directory to the target directory.
    """
    source_path = os.path.join(download_dir, file_name)
    target_path = os.path.join(target_dir, file_name)

    if not os.path.exists(source_path):
        raise FileNotFoundError(f"File not found: {source_path}")

    os.makedirs(target_dir, exist_ok=True)
    shutil.move(source_path, target_path)
    print(f"Moved {file_name} to {target_path}")

def process_csv_and_save_json(csv_path, output_json_path):
    """
    Read the CSV file, select the last values of each row for the required columns,
    and save the results in JSON format.
    """
    df = pd.read_csv(csv_path, delimiter='\t', encoding='latin1', header=None)
    df = df.iloc[:, [-8, -7, -5, -4, -2, -1]]  # Keep only the last columns
    df.columns = SELECTED_COLUMNS
    df["News Date"] = df["News Date"].astype(str).str[:4] + '.' + df["News Date"].astype(str).str[4:6] + '.' + df["News Date"].astype(str).str[6:]  # Assign column names
    
    records = df.to_dict(orient='records')
    with open(output_json_path, "w", encoding="utf-8") as json_file:
        json.dump(records, json_file, indent=4, ensure_ascii=False)
    
    print(f"Processed data saved as JSON: {output_json_path}")

# Main Execution
try:
    print("Fetching the latest GDELT file URL...")
    latest_file_url = get_latest_file_url(GDELT_URL)
    latest_file_name = latest_file_url.split("/")[-1]
    print(f"Latest file: {latest_file_name}")
    
    download_path = os.path.join(DOWNLOADS_DIR, latest_file_name)
    print(f"Downloading {latest_file_url}...")
    with requests.get(latest_file_url, stream=True) as r:
        r.raise_for_status()
        with open(download_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    print(f"Downloaded to {download_path}")
    
    decompressed_folder = os.path.join(DOWNLOADS_DIR, "decompressed")
    os.makedirs(decompressed_folder, exist_ok=True)
    decompress_zip_file(download_path, decompressed_folder)
    
    print("Processing decompressed files...")
    for file_name in os.listdir(decompressed_folder):
        decompressed_file_path = os.path.join(decompressed_folder, file_name)
        move_file_to_target(decompressed_folder, TARGET_DIR, file_name)
        csv_path = os.path.join(TARGET_DIR, file_name)
        json_output_path = os.path.join(TARGET_DIR, f"gdelt_{file_name.split('.')[0]}_gdelt.json")
        process_csv_and_save_json(csv_path, json_output_path)
    
    print("Process completed successfully!")
except Exception as e:
    print(f"An error occurred: {e}")
