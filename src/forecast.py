from __future__ import annotations

import json

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

from .config import FORECAST_FILE, METRICS_FILE


def build_forecast(monthly: pd.DataFrame, horizon: int = 6) -> pd.DataFrame:
    series = (
        monthly.groupby("period", as_index=False)["collected_amount"]
        .sum()
        .sort_values("period")
    )
    series["period"] = pd.to_datetime(series["period"])
    featured = _features(series)
    trainable = featured.dropna().copy()

    train = trainable.iloc[:-6]
    test = trainable.iloc[-6:]
    features = ["trend", "month_sin", "month_cos", "lag_1", "lag_12"]
    model = RandomForestRegressor(
        n_estimators=250, max_depth=7, random_state=42
    )
    model.fit(train[features], train["collected_amount"])
    test_prediction = model.predict(test[features])

    metrics = {
        "mae": round(float(mean_absolute_error(test["collected_amount"], test_prediction)), 2),
        "rmse": round(
            float(
                mean_squared_error(
                    test["collected_amount"], test_prediction
                )
                ** 0.5
            ),
            2,
        ),
        "mape": round(
            float(
                np.mean(
                    np.abs(
                        (test["collected_amount"].to_numpy() - test_prediction)
                        / test["collected_amount"].to_numpy()
                    )
                )
                * 100
            ),
            2,
        ),
    }

    model.fit(trainable[features], trainable["collected_amount"])
    history = series.copy()
    predictions: list[dict[str, object]] = []
    for _ in range(horizon):
        next_period = history["period"].max() + pd.offsets.MonthBegin(1)
        row = pd.DataFrame(
            {
                "period": [next_period],
                "collected_amount": [np.nan],
            }
        )
        candidate = _features(pd.concat([history, row], ignore_index=True)).iloc[-1:]
        value = float(model.predict(candidate[features])[0])
        predictions.append(
            {
                "period": next_period,
                "value": round(value, 2),
                "series": "Forecast",
            }
        )
        history = pd.concat(
            [
                history,
                pd.DataFrame(
                    {"period": [next_period], "collected_amount": [value]}
                ),
            ],
            ignore_index=True,
        )

    actual = series.rename(columns={"collected_amount": "value"})
    actual["series"] = "Actual"
    result = pd.concat([actual, pd.DataFrame(predictions)], ignore_index=True)
    result.to_csv(FORECAST_FILE, index=False)
    METRICS_FILE.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return result


def _features(series: pd.DataFrame) -> pd.DataFrame:
    data = series.copy()
    data["trend"] = np.arange(len(data))
    data["month_sin"] = np.sin(2 * np.pi * data["period"].dt.month / 12)
    data["month_cos"] = np.cos(2 * np.pi * data["period"].dt.month / 12)
    data["lag_1"] = data["collected_amount"].shift(1)
    data["lag_12"] = data["collected_amount"].shift(12)
    return data

