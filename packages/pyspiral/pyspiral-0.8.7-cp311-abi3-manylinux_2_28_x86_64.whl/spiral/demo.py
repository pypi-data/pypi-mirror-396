"""Demo data to play with SpiralDB"""

import functools
import time

import duckdb
import pandas as pd
import pyarrow as pa
from datasets import load_dataset

from spiral import Project, Spiral, Table


def _install_duckdb_extension(name: str, max_retries: int = 3) -> None:
    """Install and load a DuckDB extension with retry logic for flaky CI environments."""
    for attempt in range(max_retries):
        try:
            duckdb.execute(f"INSTALL {name}; LOAD {name};")
            return
        except duckdb.IOException:
            if attempt < max_retries - 1:
                time.sleep(0.5 * (attempt + 1))
            else:
                raise


@functools.lru_cache(maxsize=1)
def demo_project(sp: Spiral) -> Project:
    return sp.create_project(id_prefix="demo")


@functools.lru_cache(maxsize=1)
def images(sp: Spiral) -> Table:
    table = demo_project(sp).create_table(
        "openimages.images-v1", key_schema=pa.schema([("idx", pa.int64())]), exist_ok=False
    )

    # Load URLs from a TSV file
    df = pd.read_csv(
        "https://storage.googleapis.com/cvdf-datasets/oid/open-images-dataset-validation.tsv",
        names=["url", "size", "etag"],
        skiprows=1,
        sep="\t",
        header=None,
    )
    # For this example, we load just a few rows, but Spiral can handle many more.
    df = pa.Table.from_pandas(df[:10])
    df = df.append_column("idx", pa.array(range(len(df))))

    # Write just the metadata - lightweight and fast
    table.write(df)
    return table


@functools.lru_cache(maxsize=1)
def gharchive(sp: Spiral, limit=100, period=None) -> Table:
    if period is None:
        period = pd.Period("2023-01-01T00:00:00Z", freq="h")

    _install_duckdb_extension("httpfs")

    json_gz_url = f"https://data.gharchive.org/{period.strftime('%Y-%m-%d')}-{str(period.hour)}.json.gz"
    arrow_table = (
        duckdb.read_json(json_gz_url, union_by_name=True)
        .limit(limit)
        .select("""
        * REPLACE (
            cast(created_at AS TIMESTAMP_MS) AS created_at,
        )
        """)
        .to_arrow_table()
    )

    events = duckdb.from_arrow(arrow_table).order("created_at, id").distinct().to_arrow_table()
    events = (
        events.drop_columns("id")
        .add_column(0, "id", events["id"].cast(pa.large_string()))
        .drop_columns("created_at")
        .add_column(0, "created_at", events["created_at"].cast(pa.timestamp("ms")))
        .drop_columns("org")
    )

    key_schema = pa.schema([("created_at", pa.timestamp("ms")), ("id", pa.string_view())])
    table = demo_project(sp).create_table("gharchive.events", key_schema=key_schema, exist_ok=False)
    table.write(events, push_down_nulls=True)
    return table


@functools.lru_cache(maxsize=1)
def fineweb(sp: Spiral, limit=100) -> Table:
    table = demo_project(sp).create_table(
        "fineweb.v1", key_schema=pa.schema([("id", pa.string_view())]), exist_ok=False
    )

    ds = load_dataset("HuggingFaceFW/fineweb", "sample-10BT", streaming=True)
    data = ds["train"].take(limit)
    arrow_table = pa.Table.from_pylist(data.to_list())

    table.write(arrow_table, push_down_nulls=True)
    return table
