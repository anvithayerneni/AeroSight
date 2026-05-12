#!/usr/bin/env bash
set -e
export PYTHONPATH=.
echo "Generating openpyxl Excel business reports with charts & formulas..."
python3 reports/generator.py
echo "✅ Reports saved in reports/output/"
