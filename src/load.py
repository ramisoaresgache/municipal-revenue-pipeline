from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd
from sqlalchemy import create_engine, text

from .config import DATABASE_PATH


def load_tables(
    tables: dict[str, pd.DataFrame],
    database_url: str | None = None,
) -> str:
    url = database_url or f"sqlite:///{DATABASE_PATH.as_posix()}"
    engine = create_engine(url)
    started_at = datetime.now(timezone.utc)

    with engine.begin() as connection:
        for name, frame in tables.items():
            frame.to_sql(name, connection, if_exists="replace", index=False)

        connection.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS pipeline_runs (
                    run_at TEXT,
                    status TEXT,
                    rows_loaded INTEGER
                )
                """
            )
        )
        connection.execute(
            text(
                """
                INSERT INTO pipeline_runs (run_at, status, rows_loaded)
                VALUES (:run_at, :status, :rows_loaded)
                """
            ),
            {
                "run_at": started_at.isoformat(),
                "status": "success",
                "rows_loaded": len(tables["fact_revenue"]),
            },
        )
    return url

