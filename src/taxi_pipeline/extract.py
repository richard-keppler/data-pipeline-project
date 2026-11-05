import os
import requests

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")
DATA_DIR_RAW = os.path.join(DATA_DIR, "raw")
DATA_DIR_PROCESSED = os.path.join(DATA_DIR, "processed")
DB_PATH = os.path.join(DATA_DIR, "taxi.duckdb")

DATA_URLS = {
    "january": "https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2025-01.parquet",
    "february": "https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2025-02.parquet",
    "march": "https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2025-03.parquet",
}


def download_data(urls):
    os.makedirs(DATA_DIR_RAW, exist_ok=True)
    for month, url in urls.items():
        file_name = os.path.basename(url)
        file_path = os.path.join(DATA_DIR_RAW, file_name)
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        with open(file_path, "wb") as f:
            f.write(response.content)
        print(f"Downloaded data for {month} -> {file_path}")


if __name__ == "__main__":
    download_data(DATA_URLS)