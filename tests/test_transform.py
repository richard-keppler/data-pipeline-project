import duckdb
import pytest
from load import NAME_TABLE
from transform import RESULT_TABLE, transform_data

TEST_TRIPS = [
    ("2025-01-01 08:00:00", "2025-01-01 08:20:00", 10.00, 1),     # zählt
    ("2025-01-01 12:00:00", "2025-01-01 12:30:00", 20.50, 2),     # zählt
    ("2025-01-01 13:00:00", "2025-01-01 13:10:00", -5.00, 1),     # raus: negativer Betrag
    ("2025-01-01 14:00:00", "2025-01-01 14:10:00", 0.00, 1),      # raus: Betrag 0
    ("2025-01-01 15:00:00", "2025-01-01 15:10:00", 30.00, 3),     # raus: No charge
    ("2025-01-01 16:00:00", "2025-01-01 16:10:00", 40.00, 4),     # raus: Dispute
    ("2025-01-02 09:00:00", "2025-01-02 09:15:00", 15.00, None),  # zählt: fehlende Zahlungsart
    ("2025-01-02 23:50:00", "2025-01-03 00:10:00", 5.25, 1),      # zählt am Abholtag 02.01.
    ("2024-12-31 22:00:00", "2024-12-31 22:30:00", 99.00, 1),     # raus: vor dem Zeitraum
    ("2025-04-01 10:00:00", "2025-04-01 10:30:00", 99.00, 1),     # raus: nach dem Zeitraum
]

EXPECTED = [
    ("2025-01-01", 2, 30.50),
    ("2025-01-02", 2, 20.25),
]


@pytest.fixture
def db_path(tmp_path):
    path = str(tmp_path / "test.duckdb")
    con = duckdb.connect(path)
    con.sql(f"""
        CREATE TABLE {NAME_TABLE} (
            lpep_pickup_datetime  TIMESTAMP,
            lpep_dropoff_datetime TIMESTAMP,
            total_amount          DOUBLE,
            payment_type          BIGINT
        )
    """)
    con.executemany(f"INSERT INTO {NAME_TABLE} VALUES (?, ?, ?, ?)", TEST_TRIPS)
    con.close()
    return path

def read_result_table(db_path):
    con = duckdb.connect(db_path, read_only=True)
    rows = con.sql(f"""
        SELECT CAST(trip_date AS VARCHAR), trip_count, total_revenue
        FROM {RESULT_TABLE}
        ORDER BY trip_date
    """).fetchall()
    con.close()
    return rows

def test_daily_revenue_applies_filters_and_groups_by_pickup_day(db_path, tmp_path):
    transform_data(db_path, str(tmp_path / "processed"))

    assert read_result_table(db_path) == EXPECTED

def test_transform_is_idempotent(db_path, tmp_path):
    output_dir = str(tmp_path / "processed")
    transform_data(db_path, output_dir)
    first = read_result_table(db_path)
    transform_data(db_path, output_dir)
    second = read_result_table(db_path)
    assert first == second
