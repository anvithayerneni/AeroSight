"""
Pytest configuration and shared fixtures for AeroSight tests.
"""

import pandas as pd
import pytest

from ml.inference import InferenceEngine
from warehouse.db import get_db


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
