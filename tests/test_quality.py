import pandas as pd

from src.quality import validate


def test_validate_removes_invalid_and_duplicate_rows():
    data = pd.DataFrame(
        [
            {
                "account_id": 1,
                "period": "2025-01-01",
                "tax_type": "ABL",
                "zone": "Norte",
                "category": "Residencial",
                "issued_amount": 100,
                "collected_amount": 90,
                "due_date": "2025-01-15",
                "payment_date": "2025-01-16",
                "status": "Pagado",
            },
            {
                "account_id": 2,
                "period": "2025-01-01",
                "tax_type": "ABL",
                "zone": None,
                "category": "Residencial",
                "issued_amount": 100,
                "collected_amount": 80,
                "due_date": "2025-01-15",
                "payment_date": "2025-01-18",
                "status": "Pagado",
            },
        ]
    )

    valid, issues = validate(data)

    assert len(valid) == 1
    assert "zone_not_null" in issues["rule"].tolist()

