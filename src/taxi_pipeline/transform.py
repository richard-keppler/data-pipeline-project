import os
import duckdb
from extract import DATA_DIR_PROCESSED, DB_PATH
from load import NAME_TABLE

RESULT_TABLE = "daily_revenue"
RESULT_FILE = "daily_revenue.csv"
START_DATE = "2025-01-01" 
END_DATE = "2025-04-01"   


def transform_data(db_path, output_dir):
    con = duckdb.connect(db_path)
    con.sql(f"""
        CREATE OR REPLACE TABLE {RESULT_TABLE} AS
        SELECT
            CAST(lpep_pickup_datetime AS DATE) AS trip_date,
            COUNT(*) AS trip_count,
            ROUND(SUM(total_amount), 2) AS total_revenue
        FROM {NAME_TABLE}
        WHERE lpep_pickup_datetime >= ?
          AND lpep_pickup_datetime <  ?
          AND total_amount > 0
          AND (payment_type IS NULL OR payment_type NOT IN (3, 4))
        GROUP BY trip_date
        ORDER BY trip_date
    """, params=[START_DATE, END_DATE])
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, RESULT_FILE)
    con.sql(f"COPY {RESULT_TABLE} TO '{output_path}' (HEADER, DELIMITER ',')")
    day_count, trip_count = con.sql(f"""
        SELECT COUNT(*), SUM(trip_count)
        FROM {RESULT_TABLE}
    """).fetchall()[0]
    print(f"Transform successful! {day_count} days, {trip_count} trips -> {output_path}")
    con.close()


if __name__ == "__main__":
    transform_data(DB_PATH, DATA_DIR_PROCESSED)