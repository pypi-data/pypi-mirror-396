# src/anypoint_sdk/resources/observability.py
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Optional, Union

from .._http import HttpClient, HttpError
from .._logging import LoggerLike, default_logger


def _to_timestamp_ms(
    value: Union[str, date, datetime, int], end_of_day: bool = False
) -> int:
    """
    Convert various date/time formats to Unix timestamp in milliseconds.

    Args:
        value: Date/time value to convert
        end_of_day: If True and value is a date string or date object,
                   set time to 23:59:59.999 instead of 00:00:00

    Accepts:
    - datetime object
    - date object (converted to start/end of day UTC)
    - ISO string like "2025-01-01" or "2025-01-01T00:00:00Z"
    - Unix timestamp in milliseconds (int)
    """
    if isinstance(value, int):
        return value

    if isinstance(value, date) and not isinstance(value, datetime):
        # Convert date to datetime
        if end_of_day:
            # End of day: 23:59:59.999999
            value = datetime.combine(value, datetime.max.time()).replace(
                tzinfo=timezone.utc
            )
        else:
            # Start of day: 00:00:00
            value = datetime.combine(value, datetime.min.time()).replace(
                tzinfo=timezone.utc
            )

    if isinstance(value, datetime):
        # If naive datetime, assume UTC
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return int(value.timestamp() * 1000)

    # Try parsing ISO string
    if isinstance(value, str):
        # Try date only format first (assume UTC)
        try:
            dt = datetime.strptime(value, "%Y-%m-%d")
            dt = dt.replace(tzinfo=timezone.utc)
            if end_of_day:
                # Set to end of day
                dt = dt.replace(hour=23, minute=59, second=59, microsecond=999000)
            return int(dt.timestamp() * 1000)
        except ValueError:
            pass

        # Try ISO datetime format (exact time specified, ignore end_of_day flag)
        try:
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return int(dt.timestamp() * 1000)
        except ValueError:
            pass

    raise ValueError(
        f"Cannot convert {value!r} to timestamp. "
        "Expected datetime, date, ISO string, or int milliseconds."
    )


class Observability:
    """
    MuleSoft Observability metrics API.

    Note: The API has a maximum time range of 30 days per query.
    For larger ranges, use auto_split=True to automatically chunk the request.
    """

    def __init__(
        self, http: HttpClient, *, logger: Optional[LoggerLike] = None
    ) -> None:
        self._http = http
        self._log = logger or default_logger().child("resources.observability")

    def _query_single_range(
        self,
        org_id: str,
        env_id: str,
        api_instance_id: Union[int, str],
        start_ms: int,
        end_ms: int,
    ) -> int:
        """Execute a single metrics query for a time range."""

        # Debug: show the actual timestamps being used
        start_dt = datetime.fromtimestamp(start_ms / 1000, tz=timezone.utc)
        end_dt = datetime.fromtimestamp(end_ms / 1000, tz=timezone.utc)

        self._log.debug(
            "Querying API %s from %s (%s) to %s (%s)",
            api_instance_id,
            start_ms,
            start_dt.isoformat(),
            end_ms,
            end_dt.isoformat(),
        )

        query = (
            f'SELECT COUNT(requests) FROM "mulesoft.api" '
            f"WHERE \"sub_org.id\" = '{org_id}' "
            f"AND \"env.id\" = '{env_id}' "
            f"AND \"api.instance.id\" = '{api_instance_id}' "
            f"AND timestamp BETWEEN {start_ms} AND {end_ms}"
        )

        payload = {"query": query}

        self._log.debug("Query: %s", query)

        try:
            r = self._http.post_json(
                "/observability/api/v1/metrics:search",
                json_body=payload,
                params={"offset": 0, "limit": 1},
            )
        except HttpError as e:
            # Check for time range error
            if e.status == 400 and e.body and "timerange is too large" in str(e.body):
                raise ValueError(
                    "Time range exceeds 30 days. Use auto_split=True to handle large ranges."
                ) from e
            raise

        result = r.json() or {}
        data = result.get("data", [])

        if not data:
            return 0

        count = data[0].get("COUNT(requests)", 0)
        return int(count)

    def get_api_request_count(
        self,
        org_id: str,
        env_id: str,
        api_instance_id: Union[int, str],
        start: Union[str, date, datetime, int],
        end: Union[str, date, datetime, int],
        auto_split: bool = True,
    ) -> int:
        """
        Get the total number of requests for an API instance in a time range.

        Note: End dates are inclusive. "2025-01-31" means up to 23:59:59.999 on that day.
        The Observability API has a 30-day maximum per query. If your range is larger
        and auto_split=True (default), it will automatically split into multiple queries.

        Args:
            org_id: Organisation ID (sub_org.id)
            env_id: Environment ID
            api_instance_id: API instance ID
            start: Start time (datetime, date, "2025-01-01", or timestamp in ms)
            end: End time - INCLUSIVE (datetime, date, "2025-01-31", or timestamp in ms)
            auto_split: If True, automatically split ranges >30 days into chunks

        Returns:
            Total request count

        Example:
            # Get counts for all of January (inclusive)
            count = client.observability.get_api_request_count(
                org_id="abc-123",
                env_id="def-456",
                api_instance_id=20612480,
                start="2025-01-01",  # 00:00:00
                end="2025-01-31"     # 23:59:59.999 (inclusive!)
            )
        """
        # Convert start to beginning of day, end to end of day (inclusive)
        start_ms = _to_timestamp_ms(start, end_of_day=False)
        end_ms = _to_timestamp_ms(end, end_of_day=True)

        # Convert to datetime for range calculation
        start_dt = datetime.fromtimestamp(start_ms / 1000, tz=timezone.utc)
        end_dt = datetime.fromtimestamp(end_ms / 1000, tz=timezone.utc)

        # Check if range is within 30 days
        range_days = (end_dt - start_dt).days

        if range_days <= 30 or not auto_split:
            # Single query
            self._log.debug(
                "Querying request count for API %s in org %s env %s from %s to %s (%d days)",
                api_instance_id,
                org_id,
                env_id,
                start_dt.isoformat(),
                end_dt.isoformat(),
                range_days,
            )

            return self._query_single_range(
                org_id, env_id, api_instance_id, start_ms, end_ms
            )

        # Split into 30-day chunks
        self._log.info(
            "Splitting %d-day range into 30-day chunks for API %s",
            range_days,
            api_instance_id,
        )

        total_count = 0
        current_start = start_dt
        chunk_num = 1

        while current_start < end_dt:
            # Calculate chunk end (30 days or remaining time)
            chunk_end = min(current_start + timedelta(days=30), end_dt)

            chunk_start_ms = int(current_start.timestamp() * 1000)
            chunk_end_ms = int(chunk_end.timestamp() * 1000)

            self._log.debug(
                "Chunk %d: %s to %s",
                chunk_num,
                current_start.strftime("%Y-%m-%d %H:%M:%S"),
                chunk_end.strftime("%Y-%m-%d %H:%M:%S"),
            )

            chunk_count = self._query_single_range(
                org_id, env_id, api_instance_id, chunk_start_ms, chunk_end_ms
            )

            self._log.debug("Chunk %d count: %s", chunk_num, chunk_count)
            total_count += chunk_count

            # Move to next chunk (add 1ms to avoid overlap)
            current_start = chunk_end + timedelta(milliseconds=1)
            chunk_num += 1

        self._log.info(
            "Total request count for API %s across %d chunks: %s",
            api_instance_id,
            chunk_num - 1,
            total_count,
        )

        return total_count
