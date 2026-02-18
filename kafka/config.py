"""
AeroSight Kafka Configuration & Topic Definitions
Defines Kafka cluster brokers, streaming topics, and event JSON serialization schemas.
"""

import os

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

TOPIC_FLIGHTS = "flights"
TOPIC_FLIGHT_STATUS = "flight_status"
TOPIC_AIRPORT_EVENTS = "airport_events"
TOPIC_WEATHER_EVENTS = "weather_events"
TOPIC_BAGGAGE_EVENTS = "baggage_events"

ALL_TOPICS = [
    TOPIC_FLIGHTS,
    TOPIC_FLIGHT_STATUS,
    TOPIC_AIRPORT_EVENTS,
    TOPIC_WEATHER_EVENTS,
    TOPIC_BAGGAGE_EVENTS,
]

# JSON Schemas for Streaming Messages
SCHEMA_FLIGHT_STATUS = {
    "type": "object",
    "properties": {
        "event_id": {"type": "string"},
        "event_timestamp": {"type": "string"},
        "flight_id": {"type": "string"},
        "carrier_code": {"type": "string"},
        "flight_number": {"type": "integer"},
        "origin_airport": {"type": "string"},
        "dest_airport": {"type": "string"},
        "status": {"type": "string", "enum": ["SCHEDULED", "BOARDING", "DEPARTED", "AIRBORNE", "LANDED", "DELAYED", "CANCELLED"]},
        "dep_delay": {"type": "number"},
        "arr_delay": {"type": "number"},
        "current_gate": {"type": "string"}
    },
    "required": ["event_id", "event_timestamp", "flight_id", "status"]
}
