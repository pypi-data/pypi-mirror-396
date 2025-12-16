"""Tests for RelationshipsAPI."""

import unittest
from unittest.mock import MagicMock

from recallbricks_langchain import (
    RecallBricksClient,
    RelationshipsAPI,
    Relationship,
    RelationshipGraph,
    RelationshipTypeStats,
    ValidationError,
)


class TestRelationshipsAPI(unittest.TestCase):
    """Test cases for RelationshipsAPI."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = MagicMock(spec=RecallBricksClient)
        self.api = RelationshipsAPI(self.client)

    def test_get_for_memory(self):
        """Test getting relationships for a memory."""
        self.client.get.return_value = {
            "relationships": [
                {
                    "id": "rel-1",
                    "from_memory_id": "mem-1",
                    "to_memory_id": "mem-2",
                    "type": "related_to",
                    "strength": 0.85,
                    "explanation": "Semantically similar",
                },
            ],
        }

        result = self.api.get_for_memory("mem-1")

        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], Relationship)
        self.assertEqual(result[0].type, "related_to")
        self.assertEqual(result[0].strength, 0.85)

    def test_get_for_memory_validates_id(self):
        """Test that get_for_memory validates memory_id."""
        with self.assertRaises(ValidationError):
            self.api.get_for_memory("")

    def test_get_for_memory_with_filters(self):
        """Test getting relationships with filters."""
        self.client.get.return_value = {"relationships": []}

        self.api.get_for_memory("mem-1", type="caused_by", min_strength=0.7)

        self.client.get.assert_called_with(
            "/relationships/memory/mem-1",
            params={"limit": 50, "type": "caused_by", "minStrength": 0.7},
            user_id=None,
        )

    def test_get_graph(self):
        """Test getting relationship graph."""
        self.client.get.return_value = {
            "memoryId": "mem-1",
            "nodes": [
                {"id": "mem-1", "text": "Node 1"},
                {"id": "mem-2", "text": "Node 2"},
            ],
            "edges": [
                {"from": "mem-1", "to": "mem-2", "type": "related_to"},
            ],
            "depth": 2,
        }

        result = self.api.get_graph("mem-1", depth=2)

        self.assertIsInstance(result, RelationshipGraph)
        self.assertEqual(result.memory_id, "mem-1")
        self.assertEqual(len(result.nodes), 2)
        self.assertEqual(len(result.edges), 1)

    def test_get_type_stats(self):
        """Test getting relationship type statistics."""
        self.client.get.return_value = {
            "types": [
                {"type": "related_to", "count": 100, "avg_strength": 0.75},
                {"type": "caused_by", "count": 50, "avg_strength": 0.85},
            ],
        }

        result = self.api.get_type_stats()

        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], RelationshipTypeStats)
        self.assertEqual(result[0].type, "related_to")
        self.assertEqual(result[0].count, 100)

    def test_delete(self):
        """Test deleting a relationship."""
        self.client.delete.return_value = {}

        result = self.api.delete("rel-123")

        self.assertTrue(result)
        self.client.delete.assert_called_with("/relationships/rel-123", user_id=None)

    def test_delete_validates_id(self):
        """Test that delete validates relationship_id."""
        with self.assertRaises(ValidationError):
            self.api.delete("")

    def test_health(self):
        """Test relationship service health check."""
        self.client.get.return_value = {"status": "healthy"}

        result = self.api.health()

        self.assertEqual(result["status"], "healthy")


if __name__ == "__main__":
    unittest.main()
