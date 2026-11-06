from prefect import task, flow
from extract import download_data, DATA_DIR_RAW, DATA_DIR_PROCESSED, DB_PATH, DATA_URLS
from load import load_data
from transform import transform_data

@task
def extract_data_prefect(urls):
    download_data(urls)

@task
def load_data_prefect(data_dir_raw, db_path):
    load_data(data_dir_raw, db_path)

@task
def transform_data_prefect(db_path, output_dir):
    transform_data(db_path, output_dir)

@flow
def elt_pipeline(data_urls, data_dir_raw, db_path, output_dir):
    extract_data_prefect(data_urls)
    load_data_prefect(data_dir_raw, db_path)
    transform_data_prefect(db_path, output_dir)


if __name__ == "__main__":
    elt_pipeline(DATA_URLS, DATA_DIR_RAW, DB_PATH, DATA_DIR_PROCESSED)