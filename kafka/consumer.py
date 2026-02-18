"""
AeroSight Kafka Python Consumer
Reads and logs messages from aviation topics.
"""

import json
import argparse
from kafka.config import KAFKA_BOOTSTRAP_SERVERS, TOPIC_FLIGHT_STATUS

def run_consumer(topic: str = TOPIC_FLIGHT_STATUS, bootstrap_servers: str = KAFKA_BOOTSTRAP_SERVERS):
    try:
        try:
            from kafka_python_ng import KafkaConsumer
        except ImportError:
            from kafka import KafkaConsumer
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=bootstrap_servers,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            auto_offset_reset="latest",
            enable_auto_commit=True
        )
        print(f"Listening on Kafka topic '{topic}' at {bootstrap_servers}...")
        for message in consumer:
            print(f"[{message.topic}] Key: {message.key} | Value: {message.value}")
    except Exception as e:
        print(f"Kafka consumer error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AeroSight Kafka Consumer")
    parser.add_argument("--topic", type=str, default=TOPIC_FLIGHT_STATUS)
    parser.add_argument("--bootstrap-servers", type=str, default=KAFKA_BOOTSTRAP_SERVERS)
    args = parser.parse_args()
    run_consumer(topic=args.topic, bootstrap_servers=args.bootstrap_servers)
