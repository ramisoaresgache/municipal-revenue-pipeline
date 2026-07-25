from __future__ import annotations

import pandas as pd


REQUIRED_COLUMNS = {
    "account_id",
    "period",
    "tax_type",
    "zone",
    "category",
    "issued_amount",
    "collected_amount",
    "due_date",
    "payment_date",
    "status",
}
UNIQUE_KEY = ["account_id", "period", "tax_type"]


def validate(data: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    missing_columns = REQUIRED_COLUMNS.difference(data.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {sorted(missing_columns)}")

    issue_frames: list[pd.DataFrame] = []

    def add_issues(mask: pd.Series, rule: str) -> None:
        if mask.any():
            frame = data.loc[mask, UNIQUE_KEY].copy()
            frame["rule"] = rule
            issue_frames.append(frame)

    add_issues(data["zone"].isna(), "zone_not_null")
    add_issues(data["issued_amount"] <= 0, "issued_amount_positive")
    add_issues(data["collected_amount"] < 0, "collected_amount_non_negative")
    add_issues(
        data["collected_amount"] > data["issued_amount"],
        "collected_not_greater_than_issued",
    )
    add_issues(data.duplicated(UNIQUE_KEY, keep=False), "unique_business_key")

    invalid_mask = (
        data["zone"].isna()
        | (data["issued_amount"] <= 0)
        | (data["collected_amount"] < 0)
        | (data["collected_amount"] > data["issued_amount"])
        | data.duplicated(UNIQUE_KEY, keep=False)
    )
    issues = (
        pd.concat(issue_frames, ignore_index=True)
        if issue_frames
        else pd.DataFrame(columns=UNIQUE_KEY + ["rule"])
    )
    return data.loc[~invalid_mask].copy(), issues

