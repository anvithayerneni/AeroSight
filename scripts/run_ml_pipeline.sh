#!/usr/bin/env bash
set -e
export PYTHONPATH=.
echo "Training ML models (Random Forest Delay Classifier, Gradient Boosting Regressor, Isolation Forest Anomaly)..."
python3 ml/train.py
echo "✅ ML Training completed!"
