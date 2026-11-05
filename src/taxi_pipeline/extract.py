import os
import requests

DATA_URLS = {
    "january": "https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2025-01.parquet",
    "february": "https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2025-02.parquet",
    "march": "https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2025-03.parquet",
}
DATA_DIR_RAW = "./data/raw"

if not os.path.exists(DATA_DIR_RAW):
    os.makedirs(DATA_DIR_RAW)


def download_data(urls):
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