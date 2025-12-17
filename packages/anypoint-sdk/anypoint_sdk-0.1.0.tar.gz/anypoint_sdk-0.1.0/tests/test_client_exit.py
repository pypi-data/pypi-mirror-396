# tests/test_client_exit.py
import unittest
from unittest.mock import MagicMock, patch

from anypoint_sdk import AnypointClient

BASE = "https://api.test.local"


class ClientExitTests(unittest.TestCase):
    def test_exit_with_exception_still_calls_close(self):
        """Test that __exit__ calls close even when exception occurs."""
        with patch(
            "anypoint_sdk.client.get_token_with_client_credentials"
        ) as mock_token:
            mock_token.return_value = MagicMock(access_token="test-token")

            client = AnypointClient.from_client_credentials(
                "test-id",
                "test-secret",
                base_url=BASE,
            )

            # Mock the close method to verify it's called
            client.close = MagicMock()

            # Use context manager with exception
            class TestException(Exception):
                pass

            try:
                with client:
                    raise TestException("test error")
            except TestException:
                pass

            # Verify close was called despite exception
            client.close.assert_called_once()

    def test_exit_suppresses_none_for_no_exception(self):
        """Test that __exit__ returns None (doesn't suppress exceptions)."""
        with patch(
            "anypoint_sdk.client.get_token_with_client_credentials"
        ) as mock_token:
            mock_token.return_value = MagicMock(access_token="test-token")

            client = AnypointClient.from_client_credentials(
                "test-id",
                "test-secret",
                base_url=BASE,
            )

            # Test that __exit__ returns None (no suppression)
            result = client.__exit__(None, None, None)
            self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
