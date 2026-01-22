"""
AeroSight Public Aviation Dataset Downloader & Guide
Provides automated fetching instructions and metadata for real-world historical aviation datasets.
"""

import os
import sys
import argparse

DATA_SOURCES = {
    "bts_transtats": {
        "name": "US Bureau of Transportation Statistics (BTS) Airline On-Time Performance",
        "url": "https://www.transtats.bts.gov/DL_SelectFields.aspx?gnoyr_VQ=FGJ",
        "description": "Official US DOT on-time performance records for all domestic flights operated by large air carriers.",
        "license": "Public Domain (US Government Work)",
        "fields": ["FlightDate", "Reporting_Airline", "Origin", "Dest", "CRSDepTime", "DepTime", "DepDelay", "CRSArrTime", "ArrTime", "ArrDelay", "Cancelled", "Diverted", "Distance", "CarrierDelay", "WeatherDelay", "NASDelay", "SecurityDelay", "LateAircraftDelay"]
    },
    "kaggle_flights": {
        "name": "Kaggle 2015-2024 Flight Delay and Cancellation Dataset",
        "url": "https://www.kaggle.com/datasets/usdot/flight-delays",
        "description": "Comprehensive 5M+ flight records from US BTS.",
        "license": "CC0: Public Domain"
    },
    "ourairports": {
        "name": "OurAirports Global Airport Database",
        "url": "https://ourairports.com/data/",
        "description": "Open database of over 70,000 airports worldwide with IATA/ICAO codes, coordinates, and runways.",
        "license": "Public Domain"
    }
}

def print_dataset_info():
    print("=" * 80)
    print("AEROSIGHT AVIATION DATA PLATFORM — PUBLIC DATA SOURCES & ATTRIBUTION")
    print("=" * 80)
    for key, source in DATA_SOURCES.items():
        print(f"\n[Source]: {source['name']}")
        print(f" URL:     {source['url']}")
        print(f" License: {source['license']}")
        print(f" Details: {source['description']}")
    print("\n" + "=" * 80)
    print("HOW TO USE IN AEROSIGHT:")
    print("1. Out-of-the-box: AeroSight includes a realistic 30,000+ flight sample in data/sample/")
    print("2. Regenerate sample: python data/generate_dataset.py")
    print("3. Ingest custom BTS CSVs: Place downloaded CSV files into data/raw/ and run spark/bronze_ingestion.py")
    print("=" * 80)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AeroSight Dataset Downloader & Guide")
    parser.add_argument("--info", action="store_true", default=True, help="Display dataset sources and licenses")
    args = parser.parse_args()
    print_dataset_info()
