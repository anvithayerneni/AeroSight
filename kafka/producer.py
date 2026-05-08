"""
AeroSight Real-Time Aviation Event Replay Producer
Streams historical aviation records into Apache Kafka topics at configurable replay speeds.
"""

import argparse
import json
import os
import time
import uuid
from datetime import datetime

import pandas as pd

from kafka.config import (
    KAFKA_BOOTSTRAP_SERVERS,
    TOPIC_AIRPORT_EVENTS,
    TOPIC_FLIGHT_STATUS,
    TOPIC_WEATHER_EVENTS,
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data", "sample")

def create_kafka_producer(bootstrap_servers: str):
    """Attempts to connect to real Kafka cluster; returns None if offline."""
    try:
        try:
            from kafka_python_ng import KafkaProducer
        except ImportError:
            from kafka import KafkaProducer
        producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            key_serializer=lambda k: str(k).encode("utf-8") if k else None,
            request_timeout_ms=5000,
            max_block_ms=3000
        )
        print(f"Connected to Kafka broker at {bootstrap_servers}")
        return producer
    except Exception as e:
        print(f"Kafka broker not reachable at {bootstrap_servers}: {e}")
        print("Falling back to local simulated event stream mode.")
        return None

def stream_aviation_events(speed: float = 10.0, max_events: int = 100, bootstrap_servers: str = KAFKA_BOOTSTRAP_SERVERS):
    """
    Replays historical flight records as real-time operational events.
    `speed` controls simulation acceleration factor.
    """
    flights_file = os.path.join(DATA_DIR, "flights_sample.csv")
    if not os.path.exists(flights_file):
        raise FileNotFoundError(f"Source data file not found at {flights_file}")

    df = pd.read_csv(flights_file)
    print(f"Loaded {len(df)} historical flights for streaming replay.")
    print(f"Replay speed multiplier: {speed}x | Max events: {max_events if max_events > 0 else 'Continuous'}")

    producer = create_kafka_producer(bootstrap_servers)
    event_count = 0

    base_delay = 1.0 / max(1.0, speed)

    for idx, row in df.iterrows():
        if max_events > 0 and event_count >= max_events:
            break

        flight_id = row["flight_id"]
        carrier = row["carrier_code"]
        orig = row["origin_airport"]
        dest = row["dest_airport"]
        arr_delay = row["arr_delay"] if pd.notnull(row["arr_delay"]) else 0.0
        cancelled = int(row["cancelled"]) == 1
        now_ts = datetime.utcnow().isoformat()

        # 1. Flight Status Event
        status = "CANCELLED" if cancelled else ("DELAYED" if arr_delay >= 15 else "DEPARTED")
        flight_status_event = {
            "event_id": str(uuid.uuid4()),
            "event_timestamp": now_ts,
            "flight_id": flight_id,
            "carrier_code": carrier,
            "flight_number": int(row["flight_number"]),
            "origin_airport": orig,
            "dest_airport": dest,
            "status": status,
            "dep_delay": float(row["dep_delay"]) if pd.notnull(row["dep_delay"]) else 0.0,
            "arr_delay": float(arr_delay),
            "current_gate": f"G{idx % 30 + 1}",
        }

        # 2. Weather Event
        weather_event = {
            "event_id": str(uuid.uuid4()),
            "event_timestamp": now_ts,
            "airport_code": orig,
            "temperature_f": float(row["origin_temp_f"]) if pd.notnull(row["origin_temp_f"]) else 50.0,
            "wind_mph": float(row["origin_wind_mph"]) if pd.notnull(row["origin_wind_mph"]) else 5.0,
            "visibility_miles": float(row["origin_visibility_miles"]) if pd.notnull(row["origin_visibility_miles"]) else 10.0,
            "condition": str(row["origin_weather_condition"]) if pd.notnull(row["origin_weather_condition"]) else "Clear",
        }

        # 3. Airport Gate Movement Event
        airport_event = {
            "event_id": str(uuid.uuid4()),
            "event_timestamp": now_ts,
            "airport_code": orig,
            "flight_id": flight_id,
            "movement_type": "DEPARTURE_TAXI",
            "taxi_duration_min": float(row["taxi_out"]) if pd.notnull(row["taxi_out"]) else 15.0,
        }

        # Emit to Kafka or stdout
        if producer:
            try:
                producer.send(TOPIC_FLIGHT_STATUS, key=flight_id, value=flight_status_event)
                producer.send(TOPIC_WEATHER_EVENTS, key=orig, value=weather_event)
                producer.send(TOPIC_AIRPORT_EVENTS, key=orig, value=airport_event)
            except Exception as ex:
                print(f"Error publishing to Kafka: {ex}")
        
        event_count += 1
        if event_count % 10 == 0 or event_count <= 5:
            print(f"⚡ [Event #{event_count:04d}] {now_ts} | Flight {flight_id} ({carrier} {orig}->{dest}) Status: {status} | Delay: {arr_delay:+.1f}m")

        time.sleep(base_delay)

    if producer:
        producer.flush()
        producer.close()

    print(f"Successfully streamed {event_count} aviation events.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AeroSight Aviation Event Streaming Producer")
    parser.add_argument("--speed", type=float, default=10.0, help="Replay speed multiplier (default: 10)")
    parser.add_argument("--max-events", type=int, default=50, help="Max events to stream (0 for infinite)")
    parser.add_argument("--bootstrap-servers", type=str, default=KAFKA_BOOTSTRAP_SERVERS, help="Kafka bootstrap broker")
    args = parser.parse_args()

    stream_aviation_events(speed=args.speed, max_events=args.max_events, bootstrap_servers=args.bootstrap_servers)
