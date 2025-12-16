"""Tests for MonitoringAPI."""

import unittest
from unittest.mock import MagicMock

from recallbricks_langchain import (
    RecallBricksClient,
    MonitoringAPI,
    HealthCheck,
    SLAMetrics,
    AuditLogEntry,
    DashboardMetrics,
    SystemInsight,
)


class TestMonitoringAPI(unittest.TestCase):
    """Test cases for MonitoringAPI."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = MagicMock(spec=RecallBricksClient)
        self.api = MonitoringAPI(self.client)

    def test_health(self):
        """Test health check."""
        self.client.get.return_value = {
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00Z",
            "components": {
                "database": {"status": "healthy", "latency_ms": 5},
                "cache": {"status": "healthy", "latency_ms": 1},
            },
        }

        result = self.api.health()

        self.assertIsInstance(result, HealthCheck)
        self.assertEqual(result.status, "healthy")
        self.assertIn("database", result.components)

    def test_ready(self):
        """Test readiness check."""
        self.client.get.return_value = {"ready": True}

        result = self.api.ready()

        self.assertTrue(result)

    def test_ready_returns_false_on_error(self):
        """Test that ready returns False on error."""
        self.client.get.side_effect = Exception("Connection failed")

        result = self.api.ready()

        self.assertFalse(result)

    def test_live(self):
        """Test liveness check."""
        self.client.get.return_value = {"live": True}

        result = self.api.live()

        self.assertTrue(result)

    def test_get_sla(self):
        """Test getting SLA metrics."""
        self.client.get.return_value = {
            "period": "24h",
            "uptime_percent": 99.99,
            "avg_response_time_ms": 50,
            "p95_response_time_ms": 100,
            "p99_response_time_ms": 200,
            "error_rate": 0.01,
        }

        result = self.api.get_sla(period="24h")

        self.assertIsInstance(result, SLAMetrics)
        self.assertEqual(result.uptime_percent, 99.99)
        self.assertEqual(result.p99_response_time_ms, 200)

    def test_get_audit_logs(self):
        """Test getting audit logs."""
        self.client.get.return_value = {
            "logs": [
                {
                    "id": "log-1",
                    "user_id": "user-123",
                    "action_type": "memory_create",
                    "resource_id": "mem-123",
                    "timestamp": "2024-01-01T00:00:00Z",
                },
            ],
        }

        result = self.api.get_audit_logs()

        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], AuditLogEntry)
        self.assertEqual(result[0].action_type, "memory_create")

    def test_get_dashboard_metrics(self):
        """Test getting dashboard metrics."""
        self.client.get.return_value = {
            "total_memories": 10000,
            "memories_by_tier": {"tier1": 8000, "tier2": 2000},
            "total_relationships": 5000,
            "storage_used_mb": 150.5,
        }

        result = self.api.get_dashboard_metrics()

        self.assertIsInstance(result, DashboardMetrics)
        self.assertEqual(result.total_memories, 10000)
        self.assertEqual(result.memories_by_tier["tier1"], 8000)

    def test_get_insights(self):
        """Test getting system insights."""
        self.client.get.return_value = {
            "insights": [
                {
                    "id": "insight-1",
                    "insight_type": "anomaly",
                    "severity": "warning",
                    "description": "Unusual access pattern detected",
                    "resolved": False,
                },
            ],
        }

        result = self.api.get_insights()

        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], SystemInsight)
        self.assertEqual(result[0].severity, "warning")

    def test_resolve_insight(self):
        """Test resolving an insight."""
        self.client.post.return_value = {
            "id": "insight-1",
            "resolved": True,
        }

        result = self.api.resolve_insight("insight-1")

        self.assertIsInstance(result, SystemInsight)
        self.assertTrue(result.resolved)


if __name__ == "__main__":
    unittest.main()
