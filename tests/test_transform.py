import pandas as pd

from src.transform import transform


def test_transform_calculates_debt_and_collection_rate():
    data = pd.DataFrame(
        [
            {
                "account_id": 1,
                "period": "2025-01-01",
                "tax_type": "ABL",
                "zone": "Norte",
                "category": "Residencial",
                "issued_amount": 100,
                "collected_amount": 75,
                "due_date": "2025-01-15",
                "payment_date": "2025-01-20",
                "status": "Pago parcial",
            }
        ]
    )

    tables = transform(data)
    fact = tables["fact_revenue"].iloc[0]

    assert fact["debt_amount"] == 25
    assert fact["collection_rate"] == 0.75
    assert fact["days_to_payment"] == 5

