"""Tests for RecallBricksClient base client."""

import unittest
from unittest.mock import patch, MagicMock
import json
import time

from recallbricks_langchain import (
    RecallBricksClient,
    RecallBricksError,
    ValidationError,
    RateLimitError,
    AuthenticationError,
    NotFoundError,
    CircuitBreakerError,
)


class TestRecallBricksClient(unittest.TestCase):
    """Test cases for RecallBricksClient."""

    def test_init_with_api_key(self):
        """Test initialization with API key."""
        client = RecallBricksClient(api_key="test-key")
        self.assertEqual(client.api_key, "test-key")
        self.assertIsNone(client.service_token)

    def test_init_with_service_token(self):
        """Test initialization with service token."""
        client = RecallBricksClient(service_token="test-token")
        self.assertEqual(client.service_token, "test-token")
        self.assertIsNone(client.api_key)

    def test_init_without_auth_raises(self):
        """Test that initialization without auth raises error."""
        with self.assertRaises(AuthenticationError):
            RecallBricksClient()

    def test_init_requires_https(self):
        """Test that HTTP URLs are rejected."""
        with self.assertRaises(ValidationError):
            RecallBricksClient(
                api_key="test-key",
                api_url="http://api.recallbricks.com/api/v1"
            )

    @patch('recallbricks_langchain.client.get_session')
    def test_get_request(self, mock_session):
        """Test GET request."""
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_response.headers = {}
        mock_response.content = b'{"status": "ok"}'
        mock_session.return_value.request.return_value = mock_response

        client = RecallBricksClient(api_key="test-key")
        result = client.get("/health")

        self.assertEqual(result, {"status": "ok"})

    @patch('recallbricks_langchain.client.get_session')
    def test_post_request(self, mock_session):
        """Test POST request."""
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "123"}
        mock_response.headers = {}
        mock_response.content = b'{"id": "123"}'
        mock_session.return_value.request.return_value = mock_response

        client = RecallBricksClient(api_key="test-key")
        result = client.post("/memories", {"text": "test"})

        self.assertEqual(result, {"id": "123"})

    @patch('recallbricks_langchain.client.get_session')
    def test_rate_limit_headers_parsed(self, mock_session):
        """Test that rate limit headers are parsed."""
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_response.headers = {
            "X-RateLimit-Limit": "1000",
            "X-RateLimit-Remaining": "999",
        }
        mock_response.content = b'{}'
        mock_session.return_value.request.return_value = mock_response

        client = RecallBricksClient(api_key="test-key")
        client.get("/health")

        self.assertEqual(client.server_rate_limit.limit, 1000)
        self.assertEqual(client.server_rate_limit.remaining, 999)

    @patch('recallbricks_langchain.client.get_session')
    def test_auth_error_on_401(self, mock_session):
        """Test AuthenticationError on 401 response."""
        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.status_code = 401
        mock_response.json.return_value = {"error": {"message": "Invalid API key"}}
        mock_response.text = "Invalid API key"
        mock_response.headers = {}
        mock_session.return_value.request.return_value = mock_response

        client = RecallBricksClient(api_key="test-key")

        with self.assertRaises(AuthenticationError):
            client.get("/health")

    @patch('recallbricks_langchain.client.get_session')
    def test_not_found_on_404(self, mock_session):
        """Test NotFoundError on 404 response."""
        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.status_code = 404
        mock_response.json.return_value = {"error": {"message": "Not found"}}
        mock_response.text = "Not found"
        mock_response.headers = {}
        mock_session.return_value.request.return_value = mock_response

        client = RecallBricksClient(api_key="test-key")

        with self.assertRaises(NotFoundError):
            client.get("/memories/invalid-id")

    @patch('recallbricks_langchain.client.get_session')
    def test_rate_limit_on_429(self, mock_session):
        """Test RateLimitError on 429 response."""
        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.status_code = 429
        mock_response.json.return_value = {"error": {"message": "Rate limit exceeded"}}
        mock_response.text = "Rate limit exceeded"
        mock_response.headers = {"Retry-After": "60"}
        mock_session.return_value.request.return_value = mock_response

        client = RecallBricksClient(api_key="test-key")

        with self.assertRaises(RateLimitError):
            client.get("/health")

    def test_metrics_collection(self):
        """Test that metrics are collected."""
        client = RecallBricksClient(api_key="test-key", enable_metrics=True)
        metrics = client.get_metrics()

        self.assertIn("requests_total", metrics)
        self.assertIn("requests_success", metrics)

    def test_prometheus_export(self):
        """Test Prometheus metrics export."""
        client = RecallBricksClient(api_key="test-key", enable_metrics=True)
        prometheus = client.get_prometheus_metrics()

        self.assertIn("recallbricks_", prometheus)


class TestCircuitBreaker(unittest.TestCase):
    """Test cases for CircuitBreaker."""

    def test_circuit_breaker_opens_on_failures(self):
        """Test that circuit breaker opens after threshold failures."""
        from recallbricks_langchain import CircuitBreaker

        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=1)

        def failing_func():
            raise Exception("Test error")

        # Fail threshold times
        for _ in range(3):
            try:
                cb.call(failing_func)
            except Exception:
                pass

        # Circuit should be open
        self.assertEqual(cb.state, "open")

    def test_circuit_breaker_recovers(self):
        """Test that circuit breaker recovers after timeout."""
        from recallbricks_langchain import CircuitBreaker

        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.1)

        def failing_func():
            raise Exception("Test error")

        try:
            cb.call(failing_func)
        except Exception:
            pass

        # Wait for recovery
        time.sleep(0.2)

        def success_func():
            return "success"

        result = cb.call(success_func)
        self.assertEqual(result, "success")
        self.assertEqual(cb.state, "closed")


class TestRateLimiter(unittest.TestCase):
    """Test cases for RateLimiter."""

    def test_rate_limiter_allows_requests(self):
        """Test that rate limiter allows requests within limit."""
        from recallbricks_langchain import RateLimiter

        rl = RateLimiter(rate=10, per=1)

        # Should allow several requests
        for _ in range(5):
            self.assertTrue(rl.allow())

    def test_rate_limiter_blocks_excess(self):
        """Test that rate limiter blocks requests over limit."""
        from recallbricks_langchain import RateLimiter

        rl = RateLimiter(rate=2, per=1)

        # Use up allowance
        rl.allow()
        rl.allow()

        # Third should be blocked
        self.assertFalse(rl.allow())


if __name__ == "__main__":
    unittest.main()
