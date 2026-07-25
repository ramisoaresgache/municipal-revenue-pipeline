from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
QUALITY_DIR = DATA_DIR / "quality"
METRICS_DIR = DATA_DIR / "metrics"
DATABASE_PATH = DATA_DIR / "municipal_revenue.db"

RAW_FILE = RAW_DIR / "municipal_revenue_raw.csv"
POWER_BI_FILE = PROCESSED_DIR / "power_bi_revenue_monthly.csv"
FORECAST_FILE = PROCESSED_DIR / "power_bi_revenue_forecast.csv"
QUALITY_FILE = QUALITY_DIR / "quality_issues.csv"
METRICS_FILE = METRICS_DIR / "forecast_metrics.json"


def ensure_directories() -> None:
    for directory in (RAW_DIR, PROCESSED_DIR, QUALITY_DIR, METRICS_DIR):
        directory.mkdir(parents=True, exist_ok=True)

