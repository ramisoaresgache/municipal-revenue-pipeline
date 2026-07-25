from __future__ import annotations

import numpy as np
import pandas as pd

from .config import RAW_FILE, ensure_directories


TAX_TYPES = ("ABL", "TSH")
ZONES = ("Norte", "Centro", "Oeste", "Ribera")
CATEGORIES = ("Residencial", "Comercial", "Industrial")


def generate_synthetic_data(
    accounts: int = 900,
    start: str = "2022-01-01",
    periods: int = 48,
    seed: int = 42,
) -> pd.DataFrame:
    """Create fictional municipal billing and collection records."""
    rng = np.random.default_rng(seed)
    months = pd.date_range(start=start, periods=periods, freq="MS")

    account_ids = np.arange(100_000, 100_000 + accounts)
    account_tax = rng.choice(TAX_TYPES, size=accounts, p=[0.72, 0.28])
    account_zone = rng.choice(ZONES, size=accounts, p=[0.28, 0.34, 0.23, 0.15])
    account_category = rng.choice(
        CATEGORIES, size=accounts, p=[0.62, 0.28, 0.10]
    )
    account_base = rng.lognormal(mean=8.15, sigma=0.48, size=accounts)

    rows: list[pd.DataFrame] = []
    for month_number, period in enumerate(months):
        inflation = 1 + (month_number * 0.028)
        seasonal = 1 + 0.08 * np.sin(2 * np.pi * period.month / 12)
        issued = account_base * inflation * seasonal * rng.normal(1, 0.05, accounts)

        zone_effect = pd.Series(account_zone).map(
            {"Norte": 0.91, "Centro": 0.88, "Oeste": 0.82, "Ribera": 0.78}
        ).to_numpy()
        category_effect = pd.Series(account_category).map(
            {"Residencial": 0.87, "Comercial": 0.82, "Industrial": 0.79}
        ).to_numpy()
        probability = np.clip(
            (zone_effect + category_effect) / 2
            + rng.normal(0, 0.055, accounts)
            - (month_number * 0.0009),
            0.45,
            0.98,
        )
        paid = rng.random(accounts) < probability
        partial_factor = rng.uniform(0.35, 0.85, accounts)
        partial = paid & (rng.random(accounts) < 0.10)
        collected = np.where(paid, issued, 0)
        collected = np.where(partial, issued * partial_factor, collected)

        payment_delay = rng.integers(0, 50, accounts)
        due_date = period + pd.Timedelta(days=14)
        payment_date = pd.Series(
            np.where(
                paid,
                (due_date + pd.to_timedelta(payment_delay, unit="D")).strftime(
                    "%Y-%m-%d"
                ),
                None,
            )
        )

        status = np.select(
            [~paid, partial],
            ["Pendiente", "Pago parcial"],
            default="Pagado",
        )
        rows.append(
            pd.DataFrame(
                {
                    "account_id": account_ids,
                    "period": period.strftime("%Y-%m-%d"),
                    "tax_type": account_tax,
                    "zone": account_zone,
                    "category": account_category,
                    "issued_amount": np.round(issued, 2),
                    "collected_amount": np.round(collected, 2),
                    "due_date": due_date.strftime("%Y-%m-%d"),
                    "payment_date": payment_date,
                    "status": status,
                }
            )
        )

    data = pd.concat(rows, ignore_index=True)

    # Deliberate data-quality cases demonstrate the validation layer.
    data.loc[10, "zone"] = None
    data.loc[25, "issued_amount"] = -100
    data = pd.concat([data, data.iloc[[50]]], ignore_index=True)
    return data


def save_raw_data(data: pd.DataFrame) -> None:
    ensure_directories()
    data.to_csv(RAW_FILE, index=False)


if __name__ == "__main__":
    save_raw_data(generate_synthetic_data())
    print(f"Synthetic data written to {RAW_FILE}")

