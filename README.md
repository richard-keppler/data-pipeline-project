# NYC Green Taxi – Daily Revenue Pipeline

A local **ELT** pipeline that downloads the NYC Green Taxi trip records for
January–March 2025, loads them unchanged into a DuckDB database and
calculates the **revenue per day** with SQL inside the database.

```
Extract                       Load                              Transform
NYC TLC website  ──▶  data/raw/*.parquet  ──▶  data/taxi.duckdb   ──▶  daily_revenue (table)
(download)            (staging, never edited)  table: green_taxi        data/processed/daily_revenue.csv
                                               (raw, unchanged)
```

## Project Structure

```
data-pipeline-project/
├── data/
│   ├── raw/                  # staged Parquet downloads (not in Git)
│   ├── processed/            # daily_revenue.csv (not in Git)
│   └── taxi.duckdb           # DuckDB database = target system (not in Git)
├── notebooks/                # data exploration only, not part of the pipeline
├── src/taxi_pipeline/
│   ├── extract.py            # Extract: download the Parquet files; defines all paths
│   ├── load.py               # Load: raw files -> DuckDB table green_taxi
│   ├── transform.py          # Transform: green_taxi -> daily_revenue (SQL)
│   ├── pipeline.py           # Entry point: runs extract, load, transform in order
│   └── flow.py               # Prefect version (optional, not implemented)
├── tests/
│   ├── conftest.py           # puts src/taxi_pipeline on the import path for pytest
│   └── test_transform.py     # tests for the transform step
└── README.md
```

## Setup

Requires [uv](https://docs.astral.sh/uv/getting-started/installation/) 0.13.5 or newer
and Python 3.13 (see [`.python-version`](.python-version)).

```bash
git clone <repo-url>
cd data-pipeline-project
uv sync
```

## How to Run

Run all commands from the project root.

**Whole pipeline** (download, load, transform):

```bash
uv run python src/taxi_pipeline/pipeline.py
```

**Single steps:**

```bash
uv run python src/taxi_pipeline/extract.py     # download into data/raw/
uv run python src/taxi_pipeline/load.py        # load into data/taxi.duckdb
uv run python src/taxi_pipeline/transform.py   # calculate daily revenue
```

**Tests:**

```bash
uv run pytest
```

> [!NOTE]
> DuckDB allows only one process to write to `taxi.duckdb` at a time. If you get
> `Could not set lock on file`, close any open connection (e.g. in a notebook) or
> restart the notebook kernel first.

## Expected Output

```
Downloaded data for january -> .../data/raw/green_tripdata_2025-01.parquet
Downloaded data for february -> .../data/raw/green_tripdata_2025-02.parquet
Downloaded data for march -> .../data/raw/green_tripdata_2025-03.parquet
Loading successful! 146486 rows loaded into green_taxi.
Transform successful! 90 days, 144895 trips -> .../data/processed/daily_revenue.csv
```

`data/processed/daily_revenue.csv` contains one row per day:

| trip_date  | trip_count | total_revenue |
|------------|-----------:|--------------:|
| 2025-01-01 |        995 |      25068.21 |
| 2025-01-02 |       1502 |      34125.28 |
| …          |          … |             … |

The same result is stored as the table `daily_revenue` in `data/taxi.duckdb`.

## Design Decisions

### Why ELT and not ETL

The raw data is loaded **unchanged** into DuckDB (`SELECT *`), and all cleaning and
aggregation happens afterwards **inside** the database with SQL.

- The full raw data stays available in the target system. If the definition of
  revenue or a filter rule changes, only the transform step has to be re-run –
  no new download and no new load.
- DuckDB is built for analytical queries and reads Parquet directly, so the
  database does the heavy lifting instead of Python.
- DuckDB is a single local file and needs no server, which fits a local project.
- With ETL, the transformation would happen in Python (e.g. pandas) before
  loading, and only the final result would end up in the target system.

### Definition of revenue

Revenue = **`total_amount`**, which the TLC data dictionary defines as
"the total amount charged to passengers".

- It includes fares, surcharges, taxes, tolls and **credit card tips**.
- It does **not** include cash tips – they are not recorded in the data at all.
- `tip_amount` is not added on top, because credit card tips are already part of
  `total_amount` (that would count them twice).

### Cleaning rules

| Rule | Reason |
|---|---|
| A trip belongs to the day of `lpep_pickup_datetime` | the moment the meter was engaged; 1,241 trips cross midnight |
| Only pickups from 2025-01-01 to 2025-03-31 | the task asks for the first three months of 2025; 11 trips lie outside (Dec 2024, 1 Apr 2025) |
| Only `total_amount > 0` | 478 negative amounts (refunds/corrections) and 254 zero amounts are not revenue |
| Exclude `payment_type` 3 (No charge) and 4 (Dispute) | no money was collected, or it is not certain that it was |
| Keep trips with missing `payment_type` | they have normal amounts; only the payment information is missing |
| Keep very high amounts | the largest values (up to $642) belong to long trips (up to 176 miles) and are plausible |

The rules overlap. In total **1,591 of 146,486 trips (≈1.1 %)** are excluded.

### Idempotency

Every step can be run repeatedly with the same result: the download overwrites
the files, and load and transform use `CREATE OR REPLACE TABLE`.

## Review Questions

### 1. What are the steps you took to complete the project?

1. Read the brief, chose **ELT** and set up the suggested folder structure.
2. Wrote `extract.py`, which downloads the three monthly Parquet files with
   `requests` into `data/raw/`, and opened the first pull request.
3. Explored the files in a notebook with pandas (`head`, `info`, `describe`).
4. Added DuckDB and wrote `load.py`, which loads all three files unchanged into
   one table `green_taxi` (146,486 rows).
5. Explored the raw table with SQL (`SUMMARIZE`, `MIN`/`MAX`, `GROUP BY`) and used
   the TLC data dictionary to decide what revenue means and which rows to exclude.
6. Wrote `transform.py`, which calculates trip count and revenue per day and
   stores the result as a table and as a CSV file.
7. Wrote `pipeline.py` to run all steps in order, added tests and this README.
8. Used a separate branch and pull request for each step.

### 2. What challenges did you face?

- **Relative paths:** `./data/raw` points to different folders depending on where
  a script or notebook is started. I solved this by building all paths from the
  location of `extract.py` (`__file__`).
- **Imports between files and from notebooks/tests:** modules in `src/` are not on
  Python's search path by default, which caused `ModuleNotFoundError`.
- **DuckDB basics:** without `duckdb.connect(path)` everything stays in memory;
  `COPY … TO` exports a file (CSV by default) instead of creating a table; table
  names cannot be passed as `?` parameters (only values can); one process at a time
  can hold the write lock on the database file.
- **Data quality:** trips outside the requested period, negative and zero amounts,
  disputed and free trips, and `NULL` values (where `= NULL` never matches and
  `NOT IN` silently drops `NULL` rows).
- **Defining revenue:** the brief does not say which amount counts as revenue, so I
  had to read the data dictionary and make (and document) my own decision.

### 3. What would you do differently if you had more time?

- Orchestrate the pipeline with **Prefect** (`flow.py`), including retries for
  the download.
- Make the package installable (`[build-system]` in `pyproject.toml`) so imports
  work the same everywhere, without adjusting `sys.path`.
- Pass the target folder to `download_data` as a parameter instead of using a
  global constant, and add tests for extract and load.
- Add data quality checks to the pipeline itself (e.g. warn if many rows are
  filtered out) and use logging instead of `print`.
- Make the period configurable instead of hard-coding January–March 2025.
