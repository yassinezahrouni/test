import subprocess
import sys

# List of paths to the scraping code files, including the new WMO warnings file.
RSS_Data_Scraping_file_paths = [
    "Businesswire_NewsSources/Businesswire_scraping_newsarticles_fromRSSlinks.py",
    "WeatherData/Scraping_MeteoAlarms_Europe.py",
    "WeatherData/Scraping_WeatherAlerts_US_region.py",
    "WeatherData/WMO warnings/Global_WeatherWarnings_SourceWMO_craping.py"
]

# Loop through each file and run it sequentially.
for file_path in RSS_Data_Scraping_file_paths:
    print(f"Executing: {file_path} ...")
    try:
        subprocess.run([sys.executable, file_path], check=True)
        print(f"Finished executing: {file_path}\n")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while executing {file_path}: {e}")
