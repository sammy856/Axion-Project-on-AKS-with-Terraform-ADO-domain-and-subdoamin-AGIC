"""
Axion Telemetry Query Service - Database
"""

import os
import logging
from datetime import datetime, timezone
from urllib.parse import quote_plus
import asyncpg

from config import settings

logger = logging.getLogger(__name__)


def get_database_url() -> str:
    """
    Build PostgreSQL connection string from configuration.
    Username and password are injected from Azure Key Vault or environment.
    """
    if os.getenv("DATABASE_URL"):
        return os.environ["DATABASE_URL"]

    username = quote_plus(settings.POSTGRES_USER) if settings.POSTGRES_USER else "postgres"
    password = quote_plus(settings.POSTGRES_PASSWORD) if settings.POSTGRES_PASSWORD else "postgres"

    return (
        f"postgresql://{username}:{password}@"
        f"{settings.POSTGRES_HOST}:"
        f"{settings.POSTGRES_PORT}/"
        f"{settings.POSTGRES_DB}"
    )


DATABASE_URL = get_database_url()
pool: asyncpg.Pool | None = None


async def connect_to_database():
    """
    Create PostgreSQL connection pool.
    """
    global pool
    logger.info(
        "Connecting to PostgreSQL @ %s:%s/%s",
        settings.POSTGRES_HOST,
        settings.POSTGRES_PORT,
        settings.POSTGRES_DB,
    )
    pool = await asyncpg.create_pool(
        DATABASE_URL,
        min_size=1,
        max_size=10,
    )
    logger.info("Database connection pool established")


async def close_database():
    """
    Close PostgreSQL connection pool.
    """
    global pool
    if pool:
        await pool.close()
        pool = None
        logger.info("Database connection pool closed")


# Backward-compatible aliases
connect_db = connect_to_database
disconnect_db = close_database


def calculate_health(temperature: float | None, vibration: float | None) -> tuple[str, int]:
    """
    Calculate device health status and score based on telemetry.
    CRITICAL: Temperature > 100°C OR Vibration > 10 mm/s
    WARNING:  Temperature > 85°C  OR Vibration > 6 mm/s
    HEALTHY:  Otherwise
    """
    temp = temperature if temperature is not None else 0.0
    vib = vibration if vibration is not None else 0.0

    score = 100.0
    if temp > 85:
        score -= (temp - 85) * 1.0
    if vib > 6:
        score -= (vib - 6) * 3.0

    score = max(10, min(100, int(score)))

    if temp > 100 or vib > 10:
        return "critical", score
    elif temp > 85 or vib > 6:
        return "warning", score
    else:
        return "healthy", score


async def fetch_summary() -> dict:
    """
    Fetch high level summary metrics: total active devices and latest update timestamp.
    """
    if pool is None:
        raise RuntimeError("Database connection is not available")

    query = """
        SELECT 
            COUNT(DISTINCT device_id) as online_assets,
            MAX(timestamp) as last_update
        FROM telemetry;
    """
    async with pool.acquire() as conn:
        row = await conn.fetchrow(query)

    last_update_str = ""
    if row and row["last_update"]:
        dt = row["last_update"]
        last_update_str = dt.isoformat() if isinstance(dt, datetime) else str(dt)

    return {
        "onlineAssets": row["online_assets"] if row and row["online_assets"] is not None else 0,
        "lastUpdate": last_update_str,
    }


async def fetch_regions_summary() -> list[dict]:
    """
    Fetch regional summary: total devices, online devices (seen in last 2m), and alert devices.
    """
    if pool is None:
        raise RuntimeError("Database connection is not available")

    query = """
        WITH LatestDevices AS (
            SELECT DISTINCT ON (device_id)
                device_id,
                refinery_region,
                temperature,
                vibration,
                timestamp as last_seen
            FROM telemetry
            ORDER BY device_id, timestamp DESC
        )
        SELECT refinery_region, temperature, vibration, last_seen
        FROM LatestDevices;
    """
    async with pool.acquire() as conn:
        rows = await conn.fetch(query)

    regions: dict[str, dict] = {}
    now_utc = datetime.now(timezone.utc).replace(tzinfo=None)

    for r in rows:
        region = r["refinery_region"]
        if region not in regions:
            regions[region] = {"total_devices": 0, "online_devices": 0, "alert_devices": 0}

        regions[region]["total_devices"] += 1
        status, _ = calculate_health(r["temperature"], r["vibration"])

        is_online = False
        if r["last_seen"]:
            last_seen_dt = r["last_seen"]
            if isinstance(last_seen_dt, datetime):
                last_seen_naive = last_seen_dt.replace(tzinfo=None) if last_seen_dt.tzinfo else last_seen_dt
                time_diff = (now_utc - last_seen_naive).total_seconds()
                if time_diff < 120:
                    is_online = True

        if is_online:
            regions[region]["online_devices"] += 1

        if status in ["warning", "critical"]:
            regions[region]["alert_devices"] += 1

    return [
        {
            "region": k,
            "total_devices": v["total_devices"],
            "online_devices": v["online_devices"],
            "alert_devices": v["alert_devices"],
        }
        for k, v in regions.items()
    ]


async def fetch_devices() -> list[dict]:
    """
    Fetch latest state for all distinct devices.
    """
    if pool is None:
        raise RuntimeError("Database connection is not available")

    query = """
        SELECT DISTINCT ON (device_id)
            device_id,
            device_type,
            refinery_region,
            timestamp as last_seen,
            temperature,
            vibration,
            current
        FROM telemetry
        ORDER BY device_id, timestamp DESC;
    """
    async with pool.acquire() as conn:
        rows = await conn.fetch(query)

    devices = []
    for r in rows:
        d = dict(r)
        status, health_score = calculate_health(d.get("temperature"), d.get("vibration"))
        d["status"] = status
        d["health_score"] = health_score
        if isinstance(d.get("last_seen"), datetime):
            d["last_seen"] = d["last_seen"].isoformat()
        devices.append(d)

    return devices


async def fetch_top_anomalous_devices() -> list[dict]:
    """
    Fetch top anomalous devices ranked by severity.
    """
    if pool is None:
        raise RuntimeError("Database connection is not available")

    query = """
        WITH LatestDevices AS (
            SELECT DISTINCT ON (device_id)
                device_id,
                device_type,
                refinery_region,
                timestamp as last_seen,
                temperature,
                vibration,
                current
            FROM telemetry
            ORDER BY device_id, timestamp DESC
        )
        SELECT *
        FROM LatestDevices
        ORDER BY (temperature + (vibration * 10)) DESC;
    """
    async with pool.acquire() as conn:
        rows = await conn.fetch(query)

    devices = []
    for r in rows:
        d = dict(r)
        status, health_score = calculate_health(d.get("temperature"), d.get("vibration"))
        if status in ["warning", "critical"]:
            d["status"] = status
            d["health_score"] = health_score
            if isinstance(d.get("last_seen"), datetime):
                d["last_seen"] = d["last_seen"].isoformat()
            devices.append(d)
            if len(devices) == 5:
                break

    return devices


async def fetch_latest_telemetry(device_id: str | None = None) -> dict | None:
    """
    Fetch latest telemetry and metadata for a specific device.
    """
    if pool is None:
        raise RuntimeError("Database connection is not available")

    if device_id:
        query = """
            SELECT * FROM telemetry
            WHERE device_id = $1
            ORDER BY timestamp DESC
            LIMIT 1;
        """
        async with pool.acquire() as conn:
            row = await conn.fetchrow(query, device_id)
            if not row:
                return None

            d = dict(row)
            status, health_score = calculate_health(d.get("temperature"), d.get("vibration"))
            d["status"] = status
            d["health_score"] = health_score

            if "id" in d and d["id"] is not None:
                d["id"] = str(d["id"])
            if isinstance(d.get("timestamp"), datetime):
                d["timestamp"] = d["timestamp"].isoformat()
            if isinstance(d.get("created_at"), datetime):
                d["created_at"] = d["created_at"].isoformat()

            meta_query = """
                SELECT MIN(timestamp) as first_seen, COUNT(*) as total_records
                FROM telemetry
                WHERE device_id = $1;
            """
            meta_row = await conn.fetchrow(meta_query, device_id)
            if meta_row:
                first_seen = meta_row["first_seen"]
                d["first_seen"] = first_seen.isoformat() if isinstance(first_seen, datetime) else str(first_seen or "")
                d["total_records"] = meta_row["total_records"] or 0
            else:
                d["first_seen"] = None
                d["total_records"] = 0

            return d
    else:
        query = """
            SELECT * FROM telemetry
            ORDER BY timestamp DESC
            LIMIT 1;
        """
        async with pool.acquire() as conn:
            row = await conn.fetchrow(query)
            if not row:
                return None

            d = dict(row)
            status, health_score = calculate_health(d.get("temperature"), d.get("vibration"))
            d["status"] = status
            d["health_score"] = health_score

            if "id" in d and d["id"] is not None:
                d["id"] = str(d["id"])
            if isinstance(d.get("timestamp"), datetime):
                d["timestamp"] = d["timestamp"].isoformat()
            if isinstance(d.get("created_at"), datetime):
                d["created_at"] = d["created_at"].isoformat()

            return d


async def fetch_device_trends(device_id: str, hours: int = 1) -> list[dict]:
    """
    Fetch historical trend readings for a device over the given hours range.
    """
    if pool is None:
        raise RuntimeError("Database connection is not available")

    query = """
        SELECT timestamp, temperature, vibration, current
        FROM telemetry
        WHERE device_id = $1
          AND timestamp >= (
              SELECT COALESCE(MAX(timestamp), NOW() AT TIME ZONE 'UTC')
              FROM telemetry
              WHERE device_id = $1
          ) - ($2 * INTERVAL '1 hour')
        ORDER BY timestamp ASC;
    """
    async with pool.acquire() as conn:
        rows = await conn.fetch(query, device_id, hours)

    result = []
    for r in rows:
        item = dict(r)
        if isinstance(item.get("timestamp"), datetime):
            item["timestamp"] = item["timestamp"].isoformat()
        result.append(item)

    return result


async def fetch_throughput() -> list[dict]:
    """
    Fetch throughput per minute for the last hour.
    """
    if pool is None:
        raise RuntimeError("Database connection is not available")

    query = """
        SELECT
            date_trunc('minute', timestamp) as minute,
            count(*) as count
        FROM telemetry
        GROUP BY minute
        ORDER BY minute DESC
        LIMIT 60;
    """
    async with pool.acquire() as conn:
        rows = await conn.fetch(query)

    data = [dict(r) for r in rows]
    data.reverse()

    formatted = []
    for r in data:
        min_val = r["minute"]
        formatted.append({
            "minute": min_val.strftime("%H:%M") if isinstance(min_val, datetime) else str(min_val or ""),
            "count": r["count"],
        })

    return formatted
