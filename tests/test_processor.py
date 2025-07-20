import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.services import processor

import pytest
import pandas as pd
from io import StringIO
from uuid import uuid4

@pytest.fixture
def sample_csv():
    # CSV with proper test data
    csv_data = StringIO(
        """ord€r_id,curr€ncy,sku,item_price
1,USD,ABC123,10.0
2,USD,,20.0
3,USD,XYZ!@#,30.0
3,USD,XYZ!@#,30.0
,,,
"""
    )
    return csv_data


def test_clean_data(sample_csv):
    df = pd.read_csv(sample_csv)
    print(f"Original DataFrame:\n{df}")
    print(f"Malformed check: {df[['item_price', 'sku']].isnull().any(axis=1)}")
    
    cleaned_df, stats = processor.clean_data(df)
    
    print(f"Stats: {stats}")

    assert "order_id" in cleaned_df.columns
    assert "currency" in cleaned_df.columns
    assert stats["blank_rows"] == 1
    assert stats["duplicated_count"] == 1
    assert stats["sanitised_count"] == 2  # NaN becomes "nan" then gets sanitized, plus XYZ!@#
    assert stats["malformed_rows"] == 0  # Malformed check happens after blank rows removed

def test_build_metrics_returns_expected_keys():
    df = pd.DataFrame({
        "order_id": [1, 2],
        "currency": ["USD", "USD"],
        "sku": ["ABC123", "XYZ123"],
        "item_price": [10.0, 20.0]
    })
    cleaning_stats = {
        "blank_rows": 0,
        "duplicated_count": 0,
        "sanitised_count": 0,
        "malformed_rows": 0
    }
    file_id = uuid4()
    duration = 1.5

    result = processor.build_metrics(df, cleaning_stats, duration, file_id)

    assert "uploaded_at" in result
    assert "durations" in result
    assert "rows" in result
    assert "outcome" in result
    assert result["rows"]["total"] == 2
    assert result["rows"]["blank"] == 0
    assert result["rows"]["malformed"] == 0
    assert result["outcome"]["accepted"] == 2