"""
AeroSight Data Quality Rule Definitions
Specifies assertion thresholds, schema validation expectations, and business rule definitions.
"""

from typing import Any

QUALITY_RULES = {
    "required_columns": [
        "flight_id", "flight_date", "carrier_code", "flight_number",
        "origin_airport", "dest_airport", "crs_dep_time", "crs_arr_time",
        "cancelled", "diverted", "distance"
    ],
    "null_thresholds": {
        "flight_id": 0.0,
        "flight_date": 0.0,
        "carrier_code": 0.0,
        "origin_airport": 0.0,
        "dest_airport": 0.0,
        "crs_dep_time": 0.0,
        "crs_arr_time": 0.0,
        "cancelled": 0.0,
        "distance": 0.0,
    },
    "value_ranges": {
        "crs_dep_time": (0, 2359),
        "crs_arr_time": (0, 2359),
        "dep_delay": (-100, 2400),
        "arr_delay": (-100, 2400),
        "distance": (20, 10000),
        "taxi_out": (0, 300),
        "taxi_in": (0, 300),
        "air_time": (10, 1200)
    },
    "valid_cancellation_codes": ["A", "B", "C", "D", None, ""]
}

def get_rule_catalog() -> dict[str, Any]:
    """Returns the full catalog of active data quality validation rules."""
    return QUALITY_RULES
