from __future__ import annotations

import pandas as pd


def transform(data: pd.DataFrame) -> dict[str, pd.DataFrame]:
    clean = data.copy()
    for column in ("period", "due_date", "payment_date"):
        clean[column] = pd.to_datetime(clean[column], errors="coerce")

    clean["debt_amount"] = (
        clean["issued_amount"] - clean["collected_amount"]
    ).round(2)
    clean["collection_rate"] = (
        clean["collected_amount"] / clean["issued_amount"]
    ).round(4)
    clean["days_to_payment"] = (
        clean["payment_date"] - clean["due_date"]
    ).dt.days
    clean["period_key"] = clean["period"].dt.strftime("%Y%m").astype(int)

    dimensions = {
        "dim_tax": _dimension(clean, "tax_type", "tax_key"),
        "dim_zone": _dimension(clean, "zone", "zone_key"),
        "dim_category": _dimension(clean, "category", "category_key"),
    }

    fact = clean.merge(dimensions["dim_tax"], on="tax_type")
    fact = fact.merge(dimensions["dim_zone"], on="zone")
    fact = fact.merge(dimensions["dim_category"], on="category")
    fact = fact[
        [
            "account_id",
            "period_key",
            "period",
            "tax_key",
            "zone_key",
            "category_key",
            "issued_amount",
            "collected_amount",
            "debt_amount",
            "collection_rate",
            "days_to_payment",
            "status",
        ]
    ]

    monthly = (
        clean.groupby(["period", "tax_type", "zone", "category"], as_index=False)
        .agg(
            issued_amount=("issued_amount", "sum"),
            collected_amount=("collected_amount", "sum"),
            debt_amount=("debt_amount", "sum"),
            accounts=("account_id", "nunique"),
        )
        .sort_values(["period", "tax_type", "zone", "category"])
    )
    monthly["collection_rate"] = (
        monthly["collected_amount"] / monthly["issued_amount"]
    ).round(4)

    return {**dimensions, "fact_revenue": fact, "revenue_monthly": monthly}


def _dimension(data: pd.DataFrame, column: str, key: str) -> pd.DataFrame:
    values = sorted(data[column].dropna().unique())
    return pd.DataFrame({key: range(1, len(values) + 1), column: values})

