"""
AeroSight Machine Learning Training Pipeline
Trains real ML models for Flight Delay Prediction, Anomaly Detection, and Demand Forecasting.
Saves serialized artifacts and model metadata to ml/models/.
"""

import glob
import json
import os
from datetime import datetime

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor, IsolationForest, RandomForestClassifier
from sklearn.model_selection import train_test_split

from ml.evaluate import evaluate_classifier, evaluate_regressor
from ml.features import prepare_training_matrices

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GOLD_DIR = os.path.join(BASE_DIR, "data", "gold")
MODELS_DIR = os.path.join(BASE_DIR, "ml", "models")

def load_training_data() -> pd.DataFrame:
    """Loads ML feature store parquet data from Gold layer."""
    feature_files = glob.glob(os.path.join(GOLD_DIR, "ml_features", "*.parquet"))
    if not feature_files:
        raise FileNotFoundError(f"No ML feature parquet files found in {os.path.join(GOLD_DIR, 'ml_features')}")
    
    dfs = [pd.read_parquet(f) for f in feature_files]
    return pd.concat(dfs, ignore_index=True)

def train_all_models():
    os.makedirs(MODELS_DIR, exist_ok=True)
    print("=" * 60)
    print("AEROSIGHT MACHINE LEARNING PIPELINE TRAINING")
    print("=" * 60)

    # 1. Load Data
    df = load_training_data()
    print(f"Loaded {len(df):,} records from Gold ML Feature Store.")

    X, y_clf, y_reg, feature_names = prepare_training_matrices(df)
    print(f"Feature matrix shape: {X.shape}, Features: {len(feature_names)}")

    # Train / Test Split (80/20 stratified by delay flag)
    X_train, X_test, y_clf_train, y_clf_test, y_reg_train, y_reg_test = train_test_split(
        X, y_clf, y_reg, test_size=0.2, random_state=42, stratify=y_clf
    )
    print(f"Training set: {len(X_train):,} samples | Test set: {len(X_test):,} samples")

    # -----------------------------------------------------------------
    # Model 1: Flight Delay Binary Classifier (OTP-15 Prediction)
    # -----------------------------------------------------------------
    print("\n--- Training Model 1: Flight Delay Classifier (Random Forest) ---")
    clf = RandomForestClassifier(
        n_estimators=100,
        max_depth=12,
        min_samples_split=10,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )
    clf.fit(X_train, y_clf_train)

    y_pred_clf = clf.predict(X_test)
    y_prob_clf = clf.predict_proba(X_test)[:, 1]
    clf_metrics = evaluate_classifier(y_clf_test, y_pred_clf, y_prob_clf)
    print("Classifier Evaluation Results:")
    for k, v in clf_metrics.items():
        print(f"  {k}: {v}")

    # Save Classifier
    clf_path = os.path.join(MODELS_DIR, "delay_classifier.joblib")
    joblib.dump(clf, clf_path)
    print(f"✅ Saved Delay Classifier to {clf_path}")

    # Feature Importances
    importances = dict(zip(feature_names, [round(float(imp), 4) for imp in clf.feature_importances_]))
    sorted_importances = dict(sorted(importances.items(), key=lambda item: item[1], reverse=True))

    # -----------------------------------------------------------------
    # Model 2: Delay Duration Regressor (Minutes)
    # -----------------------------------------------------------------
    print("\n--- Training Model 2: Delay Duration Regressor (HistGradientBoosting) ---")
    reg = HistGradientBoostingRegressor(
        max_iter=100,
        max_depth=8,
        learning_rate=0.08,
        random_state=42
    )
    reg.fit(X_train, y_reg_train)

    y_pred_reg = reg.predict(X_test)
    reg_metrics = evaluate_regressor(y_reg_test, y_pred_reg)
    print("Regressor Evaluation Results:")
    for k, v in reg_metrics.items():
        print(f"  {k}: {v}")

    # Save Regressor
    reg_path = os.path.join(MODELS_DIR, "delay_regressor.joblib")
    joblib.dump(reg, reg_path)
    print(f"✅ Saved Delay Regressor to {reg_path}")

    # -----------------------------------------------------------------
    # Model 3: Unsupervised Operational Anomaly Detector (Isolation Forest)
    # -----------------------------------------------------------------
    print("\n--- Training Model 3: Operational Anomaly Detector (Isolation Forest) ---")
    # Features for anomaly: [dep_delay, arr_delay, taxi_out, taxi_in, speed_mph]
    anomaly_cols = ["dep_delay", "arr_delay", "taxi_out", "taxi_in"]
    X_anomaly = df[anomaly_cols].fillna(0).to_numpy(dtype=np.float32)

    iso_forest = IsolationForest(
        n_estimators=100,
        contamination=0.03, # 3% anomaly expectation
        random_state=42,
        n_jobs=-1
    )
    iso_forest.fit(X_anomaly)

    iso_path = os.path.join(MODELS_DIR, "anomaly_detector.joblib")
    joblib.dump(iso_forest, iso_path)
    print(f"✅ Saved Anomaly Detector to {iso_path}")

    # -----------------------------------------------------------------
    # Model 4: Daily Traffic Demand Forecaster Baseline
    # -----------------------------------------------------------------
    print("\n--- Training Model 4: Daily Flight Traffic Demand Forecaster ---")
    daily_traffic = df.groupby("flight_date").size().reset_index(name="flight_count")
    daily_traffic["day_idx"] = np.arange(len(daily_traffic))
    
    # Train simple linear trend + day-of-week seasonality baseline
    daily_traffic["day_of_week"] = pd.to_datetime(daily_traffic["flight_date"]).dt.dayofweek
    dow_multipliers = daily_traffic.groupby("day_of_week")["flight_count"].mean() / daily_traffic["flight_count"].mean()
    
    traffic_model_card = {
        "avg_daily_volume": round(float(daily_traffic["flight_count"].mean()), 1),
        "dow_seasonality_multipliers": dow_multipliers.round(3).to_dict(),
        "total_days_observed": len(daily_traffic)
    }

    # -----------------------------------------------------------------
    # Save Model Card & Metadata
    # -----------------------------------------------------------------
    model_card = {
        "training_timestamp": datetime.utcnow().isoformat(),
        "dataset_records": len(df),
        "features": feature_names,
        "feature_importances": sorted_importances,
        "models": {
            "delay_classifier": {
                "algorithm": "RandomForestClassifier",
                "target": "is_delayed_15",
                "metrics": clf_metrics,
                "artifact": "delay_classifier.joblib"
            },
            "delay_regressor": {
                "algorithm": "HistGradientBoostingRegressor",
                "target": "arr_delay_minutes",
                "metrics": reg_metrics,
                "artifact": "delay_regressor.joblib"
            },
            "anomaly_detector": {
                "algorithm": "IsolationForest",
                "contamination": 0.03,
                "features": anomaly_cols,
                "artifact": "anomaly_detector.joblib"
            },
            "demand_forecaster": traffic_model_card
        }
    }

    model_card_path = os.path.join(MODELS_DIR, "model_card.json")
    with open(model_card_path, "w") as f:
        json.dump(model_card, f, indent=2)
    print(f"✅ Saved Model Card to {model_card_path}")
    print("=" * 60)
    print("Machine Learning Model Training Pipeline completed successfully.")
    return model_card

if __name__ == "__main__":
    train_all_models()
