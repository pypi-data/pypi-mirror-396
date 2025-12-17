# tests/test_observability.py
import unittest
from datetime import date, datetime, timedelta, timezone

from anypoint_sdk._http import HttpClient, HttpError
from anypoint_sdk.resources.observability import Observability, _to_timestamp_ms
from tests.fakes import FakeSession
from tests.helpers import make_response

BASE = "https://api.test.local"


class TimestampConversionTests(unittest.TestCase):
    def test_converts_date_string_to_start_of_day(self):
        ts = _to_timestamp_ms("2025-01-15", end_of_day=False)
        dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
        self.assertEqual(dt.hour, 0)
        self.assertEqual(dt.minute, 0)
        self.assertEqual(dt.second, 0)

    def test_converts_date_string_to_end_of_day(self):
        ts = _to_timestamp_ms("2025-01-15", end_of_day=True)
        dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
        self.assertEqual(dt.hour, 23)
        self.assertEqual(dt.minute, 59)
        self.assertEqual(dt.second, 59)

    def test_converts_date_object_to_start_of_day(self):
        d = date(2025, 1, 15)
        ts = _to_timestamp_ms(d, end_of_day=False)
        dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
        self.assertEqual(dt.year, 2025)
        self.assertEqual(dt.month, 1)
        self.assertEqual(dt.day, 15)
        self.assertEqual(dt.hour, 0)

    def test_converts_date_object_to_end_of_day(self):
        d = date(2025, 1, 15)
        ts = _to_timestamp_ms(d, end_of_day=True)
        dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
        self.assertEqual(dt.hour, 23)
        self.assertEqual(dt.minute, 59)

    def test_converts_datetime_object(self):
        dt = datetime(2025, 1, 15, 14, 30, 0, tzinfo=timezone.utc)
        ts = _to_timestamp_ms(dt, end_of_day=False)
        result_dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
        self.assertEqual(result_dt.hour, 14)
        self.assertEqual(result_dt.minute, 30)

    def test_converts_naive_datetime_assumes_utc(self):
        dt = datetime(2025, 1, 15, 14, 30, 0)
        ts = _to_timestamp_ms(dt)
        result_dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
        self.assertEqual(result_dt.hour, 14)

    def test_passes_through_int_timestamp(self):
        ts = 1736956800000
        result = _to_timestamp_ms(ts)
        self.assertEqual(result, ts)

    def test_converts_iso_datetime_string(self):
        ts = _to_timestamp_ms("2025-01-15T14:30:00Z")
        dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
        self.assertEqual(dt.hour, 14)
        self.assertEqual(dt.minute, 30)

    def test_raises_on_invalid_input(self):
        with self.assertRaises(ValueError):
            _to_timestamp_ms("not-a-date")


class ObservabilityTests(unittest.TestCase):
    def test_get_api_request_count_single_query(self):
        org_id = "o1"
        env_id = "e1"
        api_id = 123
        payload = {"data": [{"COUNT(requests)": 42}]}

        resp = make_response(
            status=200,
            json_body=payload,
            url=f"{BASE}/observability/api/v1/metrics:search",
        )
        http = HttpClient(base_url=BASE, session=FakeSession([resp]), retries=0)
        obs = Observability(http)

        count = obs.get_api_request_count(
            org_id=org_id,
            env_id=env_id,
            api_instance_id=api_id,
            start="2025-01-01",
            end="2025-01-31",
            auto_split=False,
        )

        self.assertEqual(count, 42)

    def test_get_api_request_count_returns_zero_when_no_data(self):
        org_id = "o1"
        env_id = "e1"
        api_id = 123
        payload = {"data": []}

        resp = make_response(
            status=200,
            json_body=payload,
            url=f"{BASE}/observability/api/v1/metrics:search",
        )
        http = HttpClient(base_url=BASE, session=FakeSession([resp]), retries=0)
        obs = Observability(http)

        count = obs.get_api_request_count(
            org_id=org_id,
            env_id=env_id,
            api_instance_id=api_id,
            start="2025-01-01",
            end="2025-01-31",
            auto_split=False,
        )

        self.assertEqual(count, 0)

    def test_get_api_request_count_auto_splits_large_range(self):
        org_id = "o1"
        env_id = "e1"
        api_id = 123

        # Mock responses for 3 chunks (90 days = 3x30 day chunks)
        resp1 = make_response(
            status=200,
            json_body={"data": [{"COUNT(requests)": 10}]},
            url=f"{BASE}/observability/api/v1/metrics:search",
        )
        resp2 = make_response(
            status=200,
            json_body={"data": [{"COUNT(requests)": 20}]},
            url=f"{BASE}/observability/api/v1/metrics:search",
        )
        resp3 = make_response(
            status=200,
            json_body={"data": [{"COUNT(requests)": 30}]},
            url=f"{BASE}/observability/api/v1/metrics:search",
        )

        fake = FakeSession([resp1, resp2, resp3])
        http = HttpClient(base_url=BASE, session=fake, retries=0)
        obs = Observability(http)

        count = obs.get_api_request_count(
            org_id=org_id,
            env_id=env_id,
            api_instance_id=api_id,
            start="2025-01-01",
            end="2025-03-31",  # 90 days
            auto_split=True,
        )

        # Should sum all chunks
        self.assertEqual(count, 60)
        # Should have made 3 API calls
        self.assertEqual(len(fake.calls), 3)

    def test_get_api_request_count_raises_on_large_range_without_auto_split(self):
        org_id = "o1"
        env_id = "e1"
        api_id = 123

        # Return error for range >30 days
        resp = make_response(
            status=400,
            json_body={"message": "Queried timerange is too large"},
            url=f"{BASE}/observability/api/v1/metrics:search",
        )
        http = HttpClient(base_url=BASE, session=FakeSession([resp]), retries=0)
        obs = Observability(http)

        with self.assertRaises(ValueError) as ctx:
            obs.get_api_request_count(
                org_id=org_id,
                env_id=env_id,
                api_instance_id=api_id,
                start="2025-01-01",
                end="2025-12-31",
                auto_split=False,
            )

        self.assertIn("30 days", str(ctx.exception))

    def test_get_api_request_count_accepts_datetime_objects(self):
        org_id = "o1"
        env_id = "e1"
        api_id = 123

        now = datetime.now(tz=timezone.utc)
        yesterday = now - timedelta(days=1)

        resp = make_response(
            status=200,
            json_body={"data": [{"COUNT(requests)": 5}]},
            url=f"{BASE}/observability/api/v1/metrics:search",
        )
        http = HttpClient(base_url=BASE, session=FakeSession([resp]), retries=0)
        obs = Observability(http)

        count = obs.get_api_request_count(
            org_id=org_id,
            env_id=env_id,
            api_instance_id=api_id,
            start=yesterday,
            end=now,
            auto_split=False,
        )

        self.assertEqual(count, 5)

    def test_get_api_request_count_accepts_date_objects(self):
        org_id = "o1"
        env_id = "e1"
        api_id = 123

        start = date(2025, 1, 1)
        end = date(2025, 1, 31)

        resp = make_response(
            status=200,
            json_body={"data": [{"COUNT(requests)": 100}]},
            url=f"{BASE}/observability/api/v1/metrics:search",
        )
        http = HttpClient(base_url=BASE, session=FakeSession([resp]), retries=0)
        obs = Observability(http)

        count = obs.get_api_request_count(
            org_id=org_id,
            env_id=env_id,
            api_instance_id=api_id,
            start=start,
            end=end,
            auto_split=False,
        )

        self.assertEqual(count, 100)

    def test_get_api_request_count_accepts_timestamp_milliseconds(self):
        org_id = "o1"
        env_id = "e1"
        api_id = 123

        start_ms = 1736956800000  # 2025-01-15 00:00:00 UTC
        end_ms = 1736956800000 + (86400 * 1000)  # +1 day

        resp = make_response(
            status=200,
            json_body={"data": [{"COUNT(requests)": 7}]},
            url=f"{BASE}/observability/api/v1/metrics:search",
        )
        http = HttpClient(base_url=BASE, session=FakeSession([resp]), retries=0)
        obs = Observability(http)

        count = obs.get_api_request_count(
            org_id=org_id,
            env_id=env_id,
            api_instance_id=api_id,
            start=start_ms,
            end=end_ms,
            auto_split=False,
        )

        self.assertEqual(count, 7)

    def test_end_date_is_inclusive(self):
        org_id = "o1"
        env_id = "e1"
        api_id = 123

        resp = make_response(
            status=200,
            json_body={"data": [{"COUNT(requests)": 1}]},
            url=f"{BASE}/observability/api/v1/metrics:search",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)
        obs = Observability(http)

        obs.get_api_request_count(
            org_id=org_id,
            env_id=env_id,
            api_instance_id=api_id,
            start="2025-01-15",
            end="2025-01-15",  # Same day
            auto_split=False,
        )

        # Check the query includes end of day
        call = fake.calls[0]
        query = call["json"]["query"]
        # End timestamp should be 23:59:59.999 not 00:00:00
        self.assertIn("timestamp BETWEEN", query)
        # Extract timestamps from query
        parts = query.split("BETWEEN")[1].strip().split("AND")
        start_ts = int(parts[0].strip())
        end_ts = int(parts[1].strip())

        # End should be ~86399999ms (nearly 1 day) after start
        diff_ms = end_ts - start_ts
        # Should be close to a full day in milliseconds
        self.assertGreater(diff_ms, 86000000)  # ~24 hours


# Add these tests to tests/test_observability.py


class ObservabilityErrorHandlingTests(unittest.TestCase):
    def test_query_single_range_reraises_non_timerange_errors(self):
        """Test that non-timerange 400 errors are re-raised."""
        org_id = "o1"
        env_id = "e1"
        api_id = 123

        # Return 400 error without timerange message
        resp = make_response(
            status=400,
            json_body={"message": "Invalid query syntax"},
            url=f"{BASE}/observability/api/v1/metrics:search",
        )
        http = HttpClient(base_url=BASE, session=FakeSession([resp]), retries=0)
        obs = Observability(http)

        with self.assertRaises(HttpError) as ctx:
            obs.get_api_request_count(
                org_id=org_id,
                env_id=env_id,
                api_instance_id=api_id,
                start="2025-01-01",
                end="2025-01-31",
                auto_split=False,
            )

        # Should be HttpError, not ValueError
        self.assertEqual(ctx.exception.status, 400)

    def test_query_single_range_handles_500_errors(self):
        """Test that 500 errors are raised properly."""
        org_id = "o1"
        env_id = "e1"
        api_id = 123

        resp = make_response(
            status=500,
            json_body={"message": "Internal server error"},
            url=f"{BASE}/observability/api/v1/metrics:search",
        )
        http = HttpClient(base_url=BASE, session=FakeSession([resp]), retries=0)
        obs = Observability(http)

        with self.assertRaises(HttpError) as ctx:
            obs.get_api_request_count(
                org_id=org_id,
                env_id=env_id,
                api_instance_id=api_id,
                start="2025-01-01",
                end="2025-01-31",
                auto_split=False,
            )

        self.assertEqual(ctx.exception.status, 500)

    def test_auto_split_with_31_days_uses_single_query(self):
        """Test that exactly 30 days uses a single query."""
        org_id = "o1"
        env_id = "e1"
        api_id = 123

        resp = make_response(
            status=200,
            json_body={"data": [{"COUNT(requests)": 50}]},
            url=f"{BASE}/observability/api/v1/metrics:search",
        )
        fake = FakeSession([resp])
        http = HttpClient(base_url=BASE, session=fake, retries=0)
        obs = Observability(http)

        count = obs.get_api_request_count(
            org_id=org_id,
            env_id=env_id,
            api_instance_id=api_id,
            start="2025-01-01",
            end="2025-01-31",  # Exactly 30 days
            auto_split=True,
        )

        self.assertEqual(count, 50)
        # Should only make 1 call
        self.assertEqual(len(fake.calls), 1)

    def test_auto_split_handles_partial_final_chunk(self):
        """Test auto-split with a date range that doesn't evenly divide by 30."""
        org_id = "o1"
        env_id = "e1"
        api_id = 123

        # 45 days = 30 + 15 day chunks
        resp1 = make_response(
            status=200,
            json_body={"data": [{"COUNT(requests)": 100}]},
            url=f"{BASE}/observability/api/v1/metrics:search",
        )
        resp2 = make_response(
            status=200,
            json_body={"data": [{"COUNT(requests)": 50}]},
            url=f"{BASE}/observability/api/v1/metrics:search",
        )

        fake = FakeSession([resp1, resp2])
        http = HttpClient(base_url=BASE, session=fake, retries=0)
        obs = Observability(http)

        count = obs.get_api_request_count(
            org_id=org_id,
            env_id=env_id,
            api_instance_id=api_id,
            start="2025-01-01",
            end="2025-02-15",  # 45 days
            auto_split=True,
        )

        self.assertEqual(count, 150)
        self.assertEqual(len(fake.calls), 2)

    def test_converts_iso_datetime_with_offset(self):
        """Test ISO datetime strings with timezone offsets."""
        ts = _to_timestamp_ms("2025-01-15T14:30:00+00:00")
        dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
        self.assertEqual(dt.hour, 14)
        self.assertEqual(dt.minute, 30)

    def test_raises_on_invalid_date_format(self):
        """Test error handling for unparseable date strings."""
        with self.assertRaises(ValueError) as ctx:
            _to_timestamp_ms("15/01/2025")
        self.assertIn("Cannot convert", str(ctx.exception))

    def test_raises_on_none_input(self):
        """Test error handling for None input."""
        with self.assertRaises(ValueError):
            _to_timestamp_ms(None)  # type: ignore

    def test_raises_on_list_input(self):
        """Test error handling for wrong type input."""
        with self.assertRaises(ValueError):
            _to_timestamp_ms([2025, 1, 15])  # type: ignore


class ObservabilityLoggingTests(unittest.TestCase):
    """Test logging behavior in observability methods."""

    def test_logs_query_details(self):
        """Test that debug logging includes query details."""
        from tests.log_helper import ListLogger

        org_id = "o1"
        env_id = "e1"
        api_id = 123

        resp = make_response(
            status=200,
            json_body={"data": [{"COUNT(requests)": 10}]},
            url=f"{BASE}/observability/api/v1/metrics:search",
        )
        http = HttpClient(base_url=BASE, session=FakeSession([resp]), retries=0)

        logger = ListLogger("test")
        obs = Observability(http, logger=logger)

        obs.get_api_request_count(
            org_id=org_id,
            env_id=env_id,
            api_instance_id=api_id,
            start="2025-01-01",
            end="2025-01-31",
            auto_split=False,
        )

        # Check that query was logged
        messages = [msg for level, msg in logger.records if level == "DEBUG"]
        self.assertTrue(any("Query:" in msg for msg in messages))
        self.assertTrue(any("Querying API" in msg for msg in messages))

    def test_logs_split_info(self):
        """Test that splitting large ranges logs appropriately."""
        from tests.log_helper import ListLogger

        org_id = "o1"
        env_id = "e1"
        api_id = 123

        # 60 days splits into 3 chunks due to +1ms overlap prevention
        resp1 = make_response(
            status=200,
            json_body={"data": [{"COUNT(requests)": 10}]},
            url=f"{BASE}/observability/api/v1/metrics:search",
        )
        resp2 = make_response(
            status=200,
            json_body={"data": [{"COUNT(requests)": 20}]},
            url=f"{BASE}/observability/api/v1/metrics:search",
        )
        resp3 = make_response(
            status=200,
            json_body={"data": [{"COUNT(requests)": 5}]},
            url=f"{BASE}/observability/api/v1/metrics:search",
        )

        http = HttpClient(
            base_url=BASE, session=FakeSession([resp1, resp2, resp3]), retries=0
        )

        logger = ListLogger("test")
        obs = Observability(http, logger=logger)

        obs.get_api_request_count(
            org_id=org_id,
            env_id=env_id,
            api_instance_id=api_id,
            start="2025-01-01",
            end="2025-03-02",  # 60 days
            auto_split=True,
        )

        # Check for split logging
        messages = [msg for level, msg in logger.records if level == "INFO"]
        self.assertTrue(any("Splitting" in msg and "chunks" in msg for msg in messages))
        self.assertTrue(any("Total request count" in msg for msg in messages))


class ObservabilityEdgeCasesTests(unittest.TestCase):
    def test_empty_response_data_array_returns_zero(self):
        """Test handling of response with empty data array."""
        org_id = "o1"
        env_id = "e1"
        api_id = 123

        resp = make_response(
            status=200,
            json_body={"data": []},
            url=f"{BASE}/observability/api/v1/metrics:search",
        )
        http = HttpClient(base_url=BASE, session=FakeSession([resp]), retries=0)
        obs = Observability(http)

        count = obs.get_api_request_count(
            org_id=org_id,
            env_id=env_id,
            api_instance_id=api_id,
            start="2025-01-01",
            end="2025-01-31",
            auto_split=False,
        )

        self.assertEqual(count, 0)

    def test_response_missing_count_field_returns_zero(self):
        """Test handling of response where COUNT field is missing."""
        org_id = "o1"
        env_id = "e1"
        api_id = 123

        resp = make_response(
            status=200,
            json_body={"data": [{"other_field": "value"}]},
            url=f"{BASE}/observability/api/v1/metrics:search",
        )
        http = HttpClient(base_url=BASE, session=FakeSession([resp]), retries=0)
        obs = Observability(http)

        count = obs.get_api_request_count(
            org_id=org_id,
            env_id=env_id,
            api_instance_id=api_id,
            start="2025-01-01",
            end="2025-01-31",
            auto_split=False,
        )

        self.assertEqual(count, 0)

    def test_handles_none_json_response(self):
        """Test handling when json() returns None."""
        org_id = "o1"
        env_id = "e1"
        api_id = 123

        resp = make_response(
            status=200,
            text="",  # Empty response body
            url=f"{BASE}/observability/api/v1/metrics:search",
        )
        http = HttpClient(base_url=BASE, session=FakeSession([resp]), retries=0)
        obs = Observability(http)

        count = obs.get_api_request_count(
            org_id=org_id,
            env_id=env_id,
            api_instance_id=api_id,
            start="2025-01-01",
            end="2025-01-31",
            auto_split=False,
        )

        self.assertEqual(count, 0)


if __name__ == "__main__":
    unittest.main()
