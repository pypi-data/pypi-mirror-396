"""Tests for CollaborationAPI."""

import unittest
from unittest.mock import MagicMock

from recallbricks_langchain import (
    RecallBricksClient,
    CollaborationAPI,
    Agent,
    AgentPerformance,
    Contribution,
    Conflict,
    SynthesisResult,
    ValidationError,
)


class TestCollaborationAPI(unittest.TestCase):
    """Test cases for CollaborationAPI."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = MagicMock(spec=RecallBricksClient)
        self.api = CollaborationAPI(self.client)

    def test_register_agent(self):
        """Test agent registration."""
        self.client.post.return_value = {
            "id": "agent-123",
            "name": "Research Assistant",
            "capabilities": ["research", "summarization"],
            "reputation_score": 0.5,
        }

        result = self.api.register_agent(
            name="Research Assistant",
            capabilities=["research", "summarization"],
        )

        self.assertIsInstance(result, Agent)
        self.assertEqual(result.id, "agent-123")
        self.assertEqual(result.name, "Research Assistant")

    def test_register_agent_validates_name(self):
        """Test that register_agent validates name."""
        with self.assertRaises(ValidationError):
            self.api.register_agent("")

    def test_list_agents(self):
        """Test listing agents."""
        self.client.get.return_value = {
            "agents": [
                {"id": "agent-1", "name": "Agent 1"},
                {"id": "agent-2", "name": "Agent 2"},
            ],
        }

        result = self.api.list_agents()

        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], Agent)

    def test_get_agent_performance(self):
        """Test getting agent performance metrics."""
        self.client.get.return_value = {
            "agent_id": "agent-123",
            "total_contributions": 100,
            "accepted_contributions": 90,
            "rejected_contributions": 10,
            "avg_confidence": 0.85,
            "reputation_trend": "improving",
        }

        result = self.api.get_agent_performance("agent-123")

        self.assertIsInstance(result, AgentPerformance)
        self.assertEqual(result.total_contributions, 100)
        self.assertEqual(result.reputation_trend, "improving")

    def test_contribute(self):
        """Test agent contribution."""
        self.client.post.return_value = {
            "id": "contrib-123",
            "memory_id": "mem-123",
            "agent_id": "agent-123",
            "contribution_type": "create",
            "confidence": 0.9,
            "validation_status": "pending",
        }

        result = self.api.contribute(
            agent_id="agent-123",
            text="New finding from research",
            confidence=0.9,
        )

        self.assertIsInstance(result, Contribution)
        self.assertEqual(result.confidence, 0.9)

    def test_contribute_validates_input(self):
        """Test that contribute validates input."""
        with self.assertRaises(ValidationError):
            self.api.contribute("", "text")

        with self.assertRaises(ValidationError):
            self.api.contribute("agent-123", "")

    def test_validate_contribution(self):
        """Test validating a contribution."""
        self.client.post.return_value = {
            "id": "contrib-123",
            "validation_status": "accepted",
        }

        result = self.api.validate_contribution("contrib-123", "accepted")

        self.assertIsInstance(result, Contribution)
        self.assertEqual(result.validation_status, "accepted")

    def test_validate_contribution_invalid_status(self):
        """Test that validate_contribution rejects invalid status."""
        with self.assertRaises(ValidationError):
            self.api.validate_contribution("contrib-123", "invalid")

    def test_synthesize(self):
        """Test knowledge synthesis."""
        self.client.post.return_value = {
            "synthesized_text": "Combined insight from multiple sources",
            "source_memory_ids": ["mem-1", "mem-2", "mem-3"],
            "confidence": 0.85,
        }

        result = self.api.synthesize(["mem-1", "mem-2", "mem-3"])

        self.assertIsInstance(result, SynthesisResult)
        self.assertIn("Combined insight", result.synthesized_text)
        self.assertEqual(len(result.source_memory_ids), 3)

    def test_synthesize_requires_multiple_memories(self):
        """Test that synthesize requires at least 2 memories."""
        with self.assertRaises(ValidationError):
            self.api.synthesize(["mem-1"])

    def test_detect_conflicts(self):
        """Test conflict detection."""
        self.client.post.return_value = {
            "conflicts": [
                {
                    "id": "conflict-1",
                    "memory_id_1": "mem-1",
                    "memory_id_2": "mem-2",
                    "conflict_type": "contradiction",
                    "severity": "high",
                    "description": "Contradictory information",
                },
            ],
        }

        result = self.api.detect_conflicts()

        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], Conflict)
        self.assertEqual(result[0].conflict_type, "contradiction")

    def test_resolve_conflict(self):
        """Test resolving a conflict."""
        self.client.post.return_value = {
            "id": "conflict-1",
            "resolution_status": "resolved",
        }

        result = self.api.resolve_conflict("conflict-1", "keep_first")

        self.assertIsInstance(result, Conflict)
        self.assertEqual(result.resolution_status, "resolved")


if __name__ == "__main__":
    unittest.main()
