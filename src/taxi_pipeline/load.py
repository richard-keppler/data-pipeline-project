import os
import duckdb
from extract import DATA_DIR_RAW, DB_PATH

NAME_TABLE = "green_taxi"


def load_data(data_dir_raw, db_path):
    list_files = []
    for file in os.listdir(data_dir_raw):
        if file.endswith(".parquet"):
            list_files.append(os.path.join(data_dir_raw, file))
    con = duckdb.connect(db_path)
    con.sql(f"""
    CREATE OR REPLACE TABLE {NAME_TABLE} AS SELECT *
    FROM read_parquet(?)""", params=[list_files])
    row_count = con.sql(f"""
    SELECT COUNT(*) 
    FROM {NAME_TABLE}""").fetchall()[0][0]
    if row_count > 0:
        print(f"Loading successful! {row_count} rows loaded into {NAME_TABLE}.")
    else:
        print(f"Loading not successful! Table {NAME_TABLE} is empty.")
    con.close()


if __name__ == "__main__":
    load_data(DATA_DIR_RAW, DB_PATH)