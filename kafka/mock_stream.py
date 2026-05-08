"""
AeroSight In-Memory Real-Time Stream Generator
Provides an asynchronous streaming event generator for FastAPI Server-Sent Events (SSE)
and lightweight local development without requiring a live Kafka cluster.
"""

import asyncio
import json
import random
import uuid
from collections.abc import AsyncGenerator
from datetime import datetime
from typing import Any

CARRIERS = ["DL", "AA", "UA", "WN", "AS", "B6", "NK", "OO"]
AIRPORTS = ["ATL", "ORD", "DFW", "DEN", "LAX", "JFK", "SFO", "SEA", "MIA", "BOS", "EWR", "MCO"]

async def generate_live_aviation_event() -> dict[str, Any]:
    """Generates a realistic live telemetry event."""
    carrier = random.choice(CARRIERS)
    orig, dest = random.sample(AIRPORTS, 2)
    flight_num = random.randint(100, 2800)
    
    # 80% on-time, 18% delayed, 2% cancelled
    rand = random.random()
    if rand < 0.78:
        status = "ON-TIME"
        dep_delay = round(random.gauss(-2, 3), 1)
        arr_delay = round(dep_delay + random.gauss(-1, 4), 1)
    elif rand < 0.97:
        status = "DELAYED"
        dep_delay = round(random.exponential(25) + 15, 1)
        arr_delay = max(5.0, round(dep_delay - random.uniform(0, 10), 1))
    else:
        status = "CANCELLED"
        dep_delay = 0.0
        arr_delay = 0.0

    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    gate = f"{random.choice(['A', 'B', 'C', 'D', 'E'])}{random.randint(1, 45)}"

    return {
        "event_id": str(uuid.uuid4())[:8],
        "timestamp": now,
        "flight_id": f"FL-LIVE-{random.randint(1000, 9999)}",
        "carrier_code": carrier,
        "flight_number": flight_num,
        "origin_airport": orig,
        "dest_airport": dest,
        "status": status,
        "dep_delay": dep_delay,
        "arr_delay": arr_delay,
        "gate": gate,
        "altitude_ft": random.randint(28000, 39000) if status != "CANCELLED" else 0,
        "ground_speed_knots": random.randint(420, 510) if status != "CANCELLED" else 0,
    }

async def event_stream_generator(delay_seconds: float = 2.0) -> AsyncGenerator[str, None]:
    """Yields formatted SSE strings."""
    while True:
        event = await generate_live_aviation_event()
        yield f"data: {json.dumps(event)}\n\n"
        await asyncio.sleep(delay_seconds)
