"""
AeroSight Data Quality Reporter
Generates markdown scorecards and summary reports from validation results.
"""

import os
import json
from typing import Dict, Any

class DataQualityReporter:
    def __init__(self, validation_results: Dict[str, Any]):
        self.results = validation_results

    def generate_console_summary(self) -> str:
        """Returns concise ASCII report summary."""
        res = self.results
        status = "PASSED" if res.get("passed", False) else "FAILED"
        lines = [
            "==================================================",
            f"       AEROSIGHT DATA QUALITY SCORECARD",
            "==================================================",
            f" Dataset:          {res.get('dataset_name', 'Unknown')}",
            f" Status:           {status}",
            f" Rows Processed:   {res.get('total_rows', 0):,}",
            f" Valid Rows:       {res.get('valid_rows', 0):,}",
            f" Invalid Rows:     {res.get('invalid_rows', 0):,}",
            f" Quality Score:    {res.get('quality_score', 0.0):.2f}%",
            "--------------------------------------------------",
        ]
        checks = res.get("checks", {})
        for check_name, check_data in checks.items():
            chk_status = "PASS" if check_data.get("passed", False) else "WARN/FAIL"
            lines.append(f" {check_name:<25} : [{chk_status}]")
        lines.append("==================================================")
        return "\n".join(lines)

    def generate_markdown_report(self) -> str:
        """Generates formal markdown report suitable for pipeline documentation."""
        res = self.results
        status_badge = "✅ PASSED" if res.get("passed", False) else "❌ FAILED"
        md = f"""# AeroSight Data Quality Report — {res.get('dataset_name', 'Dataset')}

## Executive Summary
* **Status**: {status_badge}
* **Quality Score**: `{res.get('quality_score', 0.0):.2f}%`
* **Total Rows Processed**: `{res.get('total_rows', 0):,}`
* **Conforming Valid Records**: `{res.get('valid_rows', 0):,}`
* **Quarantined Records**: `{res.get('invalid_rows', 0):,}`

---

## Detailed Check Results

| Check Category | Status | Details |
| :--- | :--- | :--- |
"""
        for check_name, check_data in res.get("checks", {}).items():
            status_icon = "🟢 Pass" if check_data.get("passed", False) else "🔴 Flagged"
            details = json.dumps(check_data, indent=None)
            md += f"| `{check_name}` | {status_icon} | <pre>{details}</pre> |\n"

        return md

    def save_report(self, output_path: str):
        """Saves markdown or JSON report to disk."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        if output_path.endswith(".json"):
            with open(output_path, "w") as f:
                json.dump(self.results, f, indent=2)
        else:
            with open(output_path, "w") as f:
                f.write(self.generate_markdown_report())
