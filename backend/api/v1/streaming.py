"""
AeroSight Real-Time Streaming Telemetry Endpoints (Server-Sent Events)
"""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from kafka.mock_stream import event_stream_generator, generate_live_aviation_event

router = APIRouter(prefix="/streaming", tags=["Real-Time Operations"])

@router.get("/live-events", summary="Stream Real-Time Flight Operational Telemetry (SSE)")
async def stream_live_telemetry():
    """Returns an infinite Server-Sent Events stream of flight events."""
    return StreamingResponse(
        event_stream_generator(delay_seconds=2.5),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        }
    )

@router.get("/latest-event", summary="Get Single Latest Simulated Telemetry Event")
async def get_single_live_event():
    return await generate_live_aviation_event()
