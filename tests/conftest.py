"""
Pytest configuration and shared fixtures for AeroSight tests.
"""

import os
import pytest
import pandas as pd
from warehouse.db import get_db, DatabaseManager
from ml.inference import InferenceEngine

@pytest.fixture(scope="session")
def db():
    return get_db()

@pytest.fixture(scope="session")
def inference_engine():
    return InferenceEngine.get_instance()

@pytest.fixture
def sample_flight_data():
    df = pd.read_csv("data/sample/flights_sample.csv")
    return df.head(100)
