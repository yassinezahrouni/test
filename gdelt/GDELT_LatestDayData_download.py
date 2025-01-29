import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime
import shutil
import zipfile

# Define the GDELT URL and target folder
GDELT_URL = "http://data.gdeltproject.org/events/index.html"
DOWNLOADS_DIR = os.path.expanduser("~/Downloads")  # Default downloads directory
TARGET_DIR = "/Users/yassinezahrouni/coding/test/NewsData"

def get_latest_file_url(base_url):
    """
    Scrape the GDELT page and identify the latest file URL based on the naming convention.
    Args:
        base_url (str): The URL of the GDELT index page.
    Returns:
        str: The URL of the latest file.
    """
    response = requests.get(base_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Find all links ending with .zip
    files = []
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if href.endswith(".zip"):
            try:
                # Extract the date from the filename (e.g., 20241215 from 20241215.export.CSV.zip)
                date_str = href.split(".")[0]
                date_obj = datetime.strptime(date_str, "%Y%m%d")
                files.append((date_obj, urljoin(base_url, href)))
            except ValueError:
                continue

    # Sort files by date in descending order and return the latest one
    latest_file = max(files, key=lambda x: x[0])
    return latest_file[1]

def decompress_zip_file(zip_path, extract_to):
    """
    Decompress a zip file.
    Args:
        zip_path (str): The path of the zip file to decompress.
        extract_to (str): The directory where the files will be extracted.
    """
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print(f"Decompressed {zip_path} to {extract_to}")

def move_file_to_target(download_dir, target_dir, file_name):
    """
    Move a file from the Downloads directory to the target directory.
    Args:
        download_dir (str): The source directory.
        target_dir (str): The destination directory.
        file_name (str): The name of the file to move.
    """
    source_path = os.path.join(download_dir, file_name)
    target_path = os.path.join(target_dir, file_name)

    if not os.path.exists(source_path):
        raise FileNotFoundError(f"File not found: {source_path}")

    os.makedirs(target_dir, exist_ok=True)  # Create target directory if it doesn't exist
    shutil.move(source_path, target_path)
    print(f"Moved {file_name} to {target_path}")

# Main Execution
try:
    print("Fetching the latest GDELT file URL...")
    latest_file_url = get_latest_file_url(GDELT_URL)
    latest_file_name = latest_file_url.split("/")[-1]
    print(f"Latest file: {latest_file_name}")
    print(f"Downloading {latest_file_url}...")
    
    # Download the file to the Downloads directory
    download_path = os.path.join(DOWNLOADS_DIR, latest_file_name)
    with requests.get(latest_file_url, stream=True) as r:
        r.raise_for_status()
        with open(download_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    print(f"Downloaded to {download_path}")
    
    # Decompress the file in the Downloads directory
    decompressed_folder = os.path.join(DOWNLOADS_DIR, "decompressed")
    os.makedirs(decompressed_folder, exist_ok=True)
    decompress_zip_file(download_path, decompressed_folder)
    
    # Move the decompressed files to the target directory
    print("Moving decompressed files to the target directory...")
    for file_name in os.listdir(decompressed_folder):
        decompressed_file_path = os.path.join(decompressed_folder, file_name)
        move_file_to_target(decompressed_folder, TARGET_DIR, file_name)
    
    print("Process completed successfully!")

except Exception as e:
    print(f"An error occurred: {e}")

