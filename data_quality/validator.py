"""
AeroSight Data Quality Validator
Executes schema validation, null checks, range validations, uniqueness, and referential integrity checks.
"""

from typing import Any

import pandas as pd

from .rules import QUALITY_RULES


class DataQualityValidator:
    def __init__(self, df: pd.DataFrame, dataset_name: str = "flights"):
        self.df = df
        self.dataset_name = dataset_name
        self.total_rows = len(df)
        self.results: dict[str, Any] = {}
        self.quarantine_indices: set = set()

    def run_all_checks(self) -> dict[str, Any]:
        """Executes all data quality assertions and returns evaluation metrics."""
        if self.total_rows == 0:
            return {"status": "FAILED", "reason": "Empty dataset", "quality_score": 0.0}

        schema_res = self.check_schema()
        null_res = self.check_null_values()
        dup_res = self.check_duplicates()
        range_res = self.check_value_ranges()
        logic_res = self.check_business_logic()

        total_checks = 5
        passed_checks = sum([
            1 if schema_res["passed"] else 0,
            1 if null_res["passed"] else 0,
            1 if dup_res["passed"] else 0,
            1 if range_res["passed"] else 0,
            1 if logic_res["passed"] else 0,
        ])

        invalid_rows = len(self.quarantine_indices)
        valid_rows = self.total_rows - invalid_rows
        quality_score = round((valid_rows / self.total_rows) * 100, 2) if self.total_rows > 0 else 0.0

        self.results = {
            "dataset_name": self.dataset_name,
            "total_rows": self.total_rows,
            "valid_rows": valid_rows,
            "invalid_rows": invalid_rows,
            "quality_score": quality_score,
            "passed": quality_score >= 95.0,
            "checks": {
                "schema_conformance": schema_res,
                "null_violations": null_res,
                "duplicate_records": dup_res,
                "range_violations": range_res,
                "business_logic_rules": logic_res
            }
        }
        return self.results

    def check_schema(self) -> dict[str, Any]:
        """Verify presence of required columns."""
        required = QUALITY_RULES["required_columns"]
        missing = [col for col in required if col not in self.df.columns]
        passed = len(missing) == 0
        return {
            "passed": passed,
            "missing_columns": missing,
            "total_required": len(required),
            "present_count": len(required) - len(missing)
        }

    def check_null_values(self) -> dict[str, Any]:
        """Verify null thresholds on mandatory fields."""
        violations = {}
        for col, max_null_pct in QUALITY_RULES["null_thresholds"].items():
            if col in self.df.columns:
                null_count = int(self.df[col].isnull().sum())
                null_pct = (null_count / self.total_rows) * 100
                if null_pct > max_null_pct:
                    violations[col] = {"null_count": null_count, "null_pct": round(null_pct, 2)}
                    # Flag rows for quarantine
                    null_idx = self.df[self.df[col].isnull()].index
                    self.quarantine_indices.update(null_idx)

        return {
            "passed": len(violations) == 0,
            "violations": violations,
            "total_null_violating_columns": len(violations)
        }

    def check_duplicates(self) -> dict[str, Any]:
        """Detect duplicate records based on primary natural key."""
        dup_count = 0
        if "flight_id" in self.df.columns:
            dups = self.df.duplicated(subset=["flight_id"], keep="first")
            dup_count = int(dups.sum())
            if dup_count > 0:
                self.quarantine_indices.update(self.df[dups].index)
        elif all(c in self.df.columns for c in ["flight_date", "carrier_code", "flight_number", "origin_airport"]):
            dups = self.df.duplicated(subset=["flight_date", "carrier_code", "flight_number", "origin_airport"], keep="first")
            dup_count = int(dups.sum())
            if dup_count > 0:
                self.quarantine_indices.update(self.df[dups].index)

        return {
            "passed": dup_count == 0,
            "duplicate_count": dup_count,
            "duplicate_pct": round((dup_count / self.total_rows) * 100, 3)
        }

    def check_value_ranges(self) -> dict[str, Any]:
        """Check numeric bounds for distance, delays, elapsed time."""
        violations = {}
        for col, (min_val, max_val) in QUALITY_RULES["value_ranges"].items():
            if col in self.df.columns:
                # Exclude nulls (e.g. for cancelled flights)
                series = self.df[col].dropna()
                out_of_bounds = series[(series < min_val) | (series > max_val)]
                out_count = len(out_of_bounds)
                if out_count > 0:
                    violations[col] = {
                        "count": out_count,
                        "min_found": float(series.min()),
                        "max_found": float(series.max()),
                        "expected_range": [min_val, max_val]
                    }
                    self.quarantine_indices.update(out_of_bounds.index)

        return {
            "passed": len(violations) == 0,
            "violations": violations
        }

    def check_business_logic(self) -> dict[str, Any]:
        """Verify domain logical constraints (e.g., origin != dest, cancelled flights have no dep_time)."""
        issues = []
        
        # Rule 1: Origin != Destination
        if "origin_airport" in self.df.columns and "dest_airport" in self.df.columns:
            same_orig_dest = self.df[self.df["origin_airport"] == self.df["dest_airport"]]
            if len(same_orig_dest) > 0:
                issues.append(f"Found {len(same_orig_dest)} flights where origin equals destination")
                self.quarantine_indices.update(same_orig_dest.index)

        # Rule 2: Cancelled flights should not have actual arrival delay
        if "cancelled" in self.df.columns and "arr_delay" in self.df.columns:
            cancelled_with_delay = self.df[(self.df["cancelled"] == 1) & (self.df["arr_delay"].notnull())]
            if len(cancelled_with_delay) > 0:
                issues.append(f"Found {len(cancelled_with_delay)} cancelled flights with non-null arrival delay")
                self.quarantine_indices.update(cancelled_with_delay.index)

        return {
            "passed": len(issues) == 0,
            "issues": issues
        }

    def get_clean_dataframe(self) -> pd.DataFrame:
        """Returns dataframe with quarantined rows removed."""
        if not self.results:
            self.run_all_checks()
        return self.df.drop(index=list(self.quarantine_indices)).reset_index(drop=True)

    def get_quarantine_dataframe(self) -> pd.DataFrame:
        """Returns quarantined invalid rows."""
        if not self.results:
            self.run_all_checks()
        return self.df.loc[list(self.quarantine_indices)].reset_index(drop=True)
