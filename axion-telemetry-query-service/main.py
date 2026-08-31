"""
Axion Telemetry Query Service - API Layer
Provides REST endpoints for device condition monitoring dashboard.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

import database
from database import (
    connect_to_database,
    close_database,
    fetch_summary,
    fetch_devices,
    fetch_latest_telemetry,
    fetch_device_trends,
    fetch_top_anomalous_devices,
    fetch_throughput,
    fetch_regions_summary,
)
from config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Telemetry Query Service, connecting to database...")
    await connect_to_database()
    yield
    # Shutdown
    logger.info("Shutting down Telemetry Query Service, closing database pool...")
    await close_database()


app = FastAPI(
    title="Axion Telemetry Query Service",
    description="API for the Axion condition monitoring dashboard",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for frontend (allows all origins, headers, and methods)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "service": "Axion Telemetry Query Service",
        "status": "running",
    }


@app.get("/health")
async def health():
    if database.pool is None:
        raise HTTPException(
            status_code=503,
            detail="Database connection is not available",
        )
    return {
        "status": "healthy",
    }


@app.get("/dashboard/summary")
async def get_summary():
    try:
        return await fetch_summary()
    except Exception as e:
        logger.error(f"Error fetching summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/dashboard/regions")
async def get_regions():
    try:
        return await fetch_regions_summary()
    except Exception as e:
        logger.error(f"Error fetching regions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/dashboard/throughput")
async def get_throughput():
    try:
        return await fetch_throughput()
    except Exception as e:
        logger.error(f"Error fetching throughput: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/devices")
async def get_devices():
    try:
        return await fetch_devices()
    except Exception as e:
        logger.error(f"Error fetching devices: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/devices/top-anomalous")
async def get_top_anomalous():
    try:
        return await fetch_top_anomalous_devices()
    except Exception as e:
        logger.error(f"Error fetching top anomalous devices: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/devices/{device_id}/latest")
async def get_latest_device_data(device_id: str):
    try:
        data = await fetch_latest_telemetry(device_id)
        if not data:
            raise HTTPException(status_code=404, detail="No telemetry found for device")
        return data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching latest telemetry for {device_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/devices/{device_id}/trends")
async def get_device_trends(
    device_id: str,
    hours: int = Query(1, description="Hours of history to fetch"),
):
    try:
        return await fetch_device_trends(device_id, hours)
    except Exception as e:
        logger.error(f"Error fetching trends for {device_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/telemetry")
async def get_telemetry():
    if database.pool is None:
        raise HTTPException(
            status_code=503,
            detail="Database connection is not available",
        )

    query = """
        SELECT *
        FROM public.telemetry
        ORDER BY timestamp DESC
        LIMIT 100;
    """
    async with database.pool.acquire() as connection:
        rows = await connection.fetch(query)

    data = []
    for row in rows:
        d = dict(row)
        if "id" in d and d["id"] is not None:
            d["id"] = str(d["id"])
        if hasattr(d.get("timestamp"), "isoformat"):
            d["timestamp"] = d["timestamp"].isoformat()
        if hasattr(d.get("created_at"), "isoformat"):
            d["created_at"] = d["created_at"].isoformat()
        data.append(d)

    return {
        "count": len(data),
        "data": data,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=True)