from extract import download_data, DATA_DIR_RAW, DATA_DIR_PROCESSED, DB_PATH, DATA_URLS
from load import load_data
from transform import transform_data


def run_pipeline(data_urls, data_dir_raw, db_path, output_dir):
    download_data(data_urls)
    load_data(data_dir_raw, db_path)
    transform_data(db_path, output_dir)


if __name__ == "__main__":
    run_pipeline(DATA_URLS, DATA_DIR_RAW, DB_PATH, DATA_DIR_PROCESSED)