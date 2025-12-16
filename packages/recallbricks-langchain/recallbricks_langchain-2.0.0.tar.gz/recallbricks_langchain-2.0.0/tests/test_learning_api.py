"""Tests for LearningAPI."""

import unittest
from unittest.mock import MagicMock

from recallbricks_langchain import (
    RecallBricksClient,
    LearningAPI,
    LearningAnalysisResult,
    LearningStatus,
    LearningMetrics,
    MaintenanceSuggestion,
)


class TestLearningAPI(unittest.TestCase):
    """Test cases for LearningAPI."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = MagicMock(spec=RecallBricksClient)
        self.api = LearningAPI(self.client)

    def test_analyze(self):
        """Test learning analysis."""
        self.client.post.return_value = {
            "result": {
                "timestamp": "2024-01-01T00:00:00Z",
                "clusters_detected": 5,
                "relationship_suggestions": [
                    {
                        "memory_id": "mem-1",
                        "related_memory_id": "mem-2",
                        "suggested_type": "related_to",
                        "confidence": 0.8,
                        "reason": "High co-access",
                        "co_access_count": 10,
                    },
                ],
                "stale_memory_count": 3,
                "processing_time_ms": 150,
            },
        }

        result = self.api.analyze()

        self.assertIsInstance(result, LearningAnalysisResult)
        self.assertEqual(result.clusters_detected, 5)
        self.assertEqual(len(result.relationship_suggestions), 1)
        self.assertEqual(result.stale_memory_count, 3)

    def test_analyze_with_auto_apply(self):
        """Test analysis with auto-apply."""
        self.client.post.return_value = {"result": {"clusters_detected": 0}}

        self.api.analyze(auto_apply=True)

        self.client.post.assert_called_with(
            "/learning/analyze",
            {"auto_apply": True},
            user_id=None,
        )

    def test_get_status(self):
        """Test getting learning system status."""
        self.client.get.return_value = {
            "enabled": True,
            "last_analysis": "2024-01-01T00:00:00Z",
            "total_analyses": 100,
            "relationships_created": 500,
        }

        result = self.api.get_status()

        self.assertIsInstance(result, LearningStatus)
        self.assertTrue(result.enabled)
        self.assertEqual(result.total_analyses, 100)

    def test_get_metrics(self):
        """Test getting learning metrics."""
        self.client.get.return_value = {
            "total_memories": 1000,
            "total_relationships": 500,
            "avg_relationships_per_memory": 0.5,
            "cluster_count": 25,
            "orphan_count": 10,
            "stale_count": 50,
        }

        result = self.api.get_metrics()

        self.assertIsInstance(result, LearningMetrics)
        self.assertEqual(result.total_memories, 1000)
        self.assertEqual(result.avg_relationships_per_memory, 0.5)

    def test_get_maintenance_suggestions(self):
        """Test getting maintenance suggestions."""
        self.client.get.return_value = {
            "suggestions": [
                {
                    "memory_id": "mem-1",
                    "suggestion_type": "archive",
                    "reason": "Not accessed in 90 days",
                    "score": 0.9,
                },
                {
                    "memory_id": "mem-2",
                    "suggestion_type": "merge",
                    "reason": "Highly similar to mem-3",
                    "score": 0.85,
                    "related_memory_ids": ["mem-3"],
                },
            ],
        }

        result = self.api.get_maintenance_suggestions()

        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], MaintenanceSuggestion)
        self.assertEqual(result[0].suggestion_type, "archive")
        self.assertEqual(result[1].suggestion_type, "merge")

    def test_apply_suggestions(self):
        """Test applying suggestions."""
        self.client.post.return_value = {"applied": 5}

        result = self.api.apply_suggestions(["sug-1", "sug-2"])

        self.assertEqual(result["applied"], 5)


if __name__ == "__main__":
    unittest.main()
