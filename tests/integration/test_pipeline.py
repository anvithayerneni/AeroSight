"""
End-to-End Pipeline Integration Test
"""

import os

from warehouse.db import get_db


def test_pipeline_data_flow():
    # 1. Verify Sample & Raw files exist
    assert os.path.exists("data/sample/flights_sample.csv")
    assert os.path.exists("data/sample/airports.csv")
    
    # 2. Verify Data Lake Gold Parquet files exist
    assert os.path.exists("data/gold/fact_flights")
    assert os.path.exists("data/gold/dim_airport")
    
    # 3. Verify ML Models serialized on disk
    assert os.path.exists("ml/models/delay_classifier.joblib")
    assert os.path.exists("ml/models/delay_regressor.joblib")
    assert os.path.exists("ml/models/model_card.json")

    # 4. Verify Warehouse query response
    db = get_db()
    res = db.execute_query("SELECT COUNT(*) as cnt FROM fact_flights")
    assert res[0]["cnt"] > 0
