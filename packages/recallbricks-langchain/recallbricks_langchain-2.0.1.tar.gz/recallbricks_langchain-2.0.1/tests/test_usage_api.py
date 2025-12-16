"""Tests for UsageAPI."""

import unittest
from unittest.mock import MagicMock

from recallbricks_langchain import (
    RecallBricksClient,
    UsageAPI,
    UsageStats,
    UsageHistoryEntry,
    UsageBreakdown,
)


class TestUsageAPI(unittest.TestCase):
    """Test cases for UsageAPI."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = MagicMock(spec=RecallBricksClient)
        self.api = UsageAPI(self.client)

    def test_get_current(self):
        """Test getting current usage."""
        self.client.get.return_value = {
            "operations_used": 5000,
            "operations_limit": 10000,
            "operations_remaining": 5000,
            "percent_used": 50.0,
            "cost_usd": "2.50",
            "in_overage": False,
            "status": "healthy",
            "plan": "pro",
            "month": "2024-01",
        }

        result = self.api.get_current()

        self.assertIsInstance(result, UsageStats)
        self.assertEqual(result.operations_used, 5000)
        self.assertEqual(result.percent_used, 50.0)
        self.assertEqual(result.status, "healthy")

    def test_get_history(self):
        """Test getting usage history."""
        self.client.get.return_value = {
            "history": [
                {"month": "2024-01", "operations_count": 8000, "cost_cents": 400},
                {"month": "2023-12", "operations_count": 7500, "cost_cents": 375},
            ],
        }

        result = self.api.get_history(months=2)

        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], UsageHistoryEntry)
        self.assertEqual(result[0].month, "2024-01")

    def test_get_breakdown(self):
        """Test getting usage breakdown."""
        self.client.get.return_value = {
            "breakdown": [
                {"event_type": "memory_create", "count": 1000, "percentage": 20.0},
                {"event_type": "memory_search", "count": 4000, "percentage": 80.0},
            ],
        }

        result = self.api.get_breakdown()

        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], UsageBreakdown)
        self.assertEqual(result[0].event_type, "memory_create")

    def test_check_limits_healthy(self):
        """Test checking limits when healthy."""
        self.client.get.return_value = {
            "status": "healthy",
            "percent_used": 50.0,
            "operations_remaining": 5000,
        }

        result = self.api.check_limits()

        self.assertTrue(result["can_proceed"])
        self.assertEqual(result["status"], "healthy")

    def test_check_limits_blocked(self):
        """Test checking limits when blocked."""
        self.client.get.return_value = {
            "status": "blocked",
            "percent_used": 100.0,
            "operations_remaining": 0,
            "message": "Usage limit exceeded",
        }

        result = self.api.check_limits()

        self.assertFalse(result["can_proceed"])
        self.assertEqual(result["status"], "blocked")


if __name__ == "__main__":
    unittest.main()
