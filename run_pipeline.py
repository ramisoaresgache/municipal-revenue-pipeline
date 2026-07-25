from __future__ import annotations

import argparse
import os

import pandas as pd

from src.config import (
    POWER_BI_FILE,
    QUALITY_FILE,
    RAW_FILE,
    ensure_directories,
)
from src.forecast import build_forecast
from src.generate_data import generate_synthetic_data, save_raw_data
from src.load import load_tables
from src.quality import validate
from src.transform import transform


def run(regenerate: bool = False) -> None:
    ensure_directories()
    if regenerate or not RAW_FILE.exists():
        print("[1/6] Generating synthetic municipal data")
        save_raw_data(generate_synthetic_data())

    print("[2/6] Extracting raw records")
    raw = pd.read_csv(RAW_FILE)

    print("[3/6] Running data-quality checks")
    valid, issues = validate(raw)
    issues.to_csv(QUALITY_FILE, index=False)

    print("[4/6] Transforming data and building dimensional model")
    tables = transform(valid)
    tables["revenue_monthly"].to_csv(POWER_BI_FILE, index=False)

    print("[5/6] Loading analytical tables")
    database_url = os.getenv("DATABASE_URL")
    loaded_url = load_tables(tables, database_url)

    print("[6/6] Training forecast and exporting Power BI datasets")
    build_forecast(tables["revenue_monthly"])

    print(
        f"Pipeline completed: {len(valid):,} valid rows, "
        f"{len(issues):,} quality findings, database={loaded_url}"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--regenerate",
        action="store_true",
        help="Replace the synthetic source data before running the pipeline.",
    )
    args = parser.parse_args()
    run(regenerate=args.regenerate)
