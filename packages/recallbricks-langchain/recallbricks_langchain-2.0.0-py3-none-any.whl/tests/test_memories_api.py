"""Tests for MemoriesAPI."""

import unittest
from unittest.mock import patch, MagicMock

from recallbricks_langchain import (
    RecallBricksClient,
    MemoriesAPI,
    Memory,
    LearnResult,
    SearchResult,
    RecallResult,
    ValidationError,
)


class TestMemoriesAPI(unittest.TestCase):
    """Test cases for MemoriesAPI."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = MagicMock(spec=RecallBricksClient)
        self.api = MemoriesAPI(self.client)

    def test_create_memory(self):
        """Test memory creation."""
        self.client.post.return_value = {
            "id": "mem-123",
            "text": "Test memory",
            "source": "api",
            "project_id": "default",
            "tags": ["test"],
            "created_at": "2024-01-01T00:00:00Z",
        }

        result = self.api.create("Test memory", tags=["test"])

        self.assertIsInstance(result, Memory)
        self.assertEqual(result.id, "mem-123")
        self.assertEqual(result.text, "Test memory")
        self.client.post.assert_called_once()

    def test_create_validates_text(self):
        """Test that create validates text input."""
        with self.assertRaises(ValidationError):
            self.api.create("")

        with self.assertRaises(ValidationError):
            self.api.create(None)

    def test_get_memory(self):
        """Test getting a memory by ID."""
        self.client.get.return_value = {
            "id": "mem-123",
            "text": "Test memory",
        }

        result = self.api.get("mem-123")

        self.assertIsInstance(result, Memory)
        self.assertEqual(result.id, "mem-123")
        self.client.get.assert_called_with("/memories/mem-123", user_id=None)

    def test_list_memories(self):
        """Test listing memories."""
        self.client.get.return_value = {
            "memories": [
                {"id": "mem-1", "text": "Memory 1"},
                {"id": "mem-2", "text": "Memory 2"},
            ],
            "count": 2,
            "total": 100,
        }

        result = self.api.list(limit=10)

        self.assertEqual(len(result["memories"]), 2)
        self.assertEqual(result["total"], 100)

    def test_list_validates_limit(self):
        """Test that list validates limit parameter."""
        with self.assertRaises(ValidationError):
            self.api.list(limit=0)

        with self.assertRaises(ValidationError):
            self.api.list(limit=101)

    def test_update_memory(self):
        """Test updating a memory."""
        self.client.put.return_value = {
            "id": "mem-123",
            "text": "Updated memory",
            "tags": ["updated"],
        }

        result = self.api.update("mem-123", text="Updated memory")

        self.assertIsInstance(result, Memory)
        self.assertEqual(result.text, "Updated memory")

    def test_update_requires_field(self):
        """Test that update requires at least one field."""
        with self.assertRaises(ValidationError):
            self.api.update("mem-123")

    def test_delete_memory(self):
        """Test deleting a memory."""
        self.client.delete.return_value = {}

        result = self.api.delete("mem-123")

        self.assertTrue(result)
        self.client.delete.assert_called_with("/memories/mem-123", user_id=None)

    def test_learn(self):
        """Test smart learning with metadata extraction."""
        self.client.post.return_value = {
            "id": "mem-123",
            "text": "User prefers dark mode",
            "extracted_metadata": {
                "category": "Preferences",
                "tags": ["ui", "preferences"],
                "importance": "medium",
                "confidence": 0.95,
            },
            "extraction_tier": 1,
            "extraction_method": "heuristic",
        }

        result = self.api.learn("User prefers dark mode")

        self.assertIsInstance(result, LearnResult)
        self.assertEqual(result.memory.id, "mem-123")
        self.assertEqual(result.extracted_metadata.category, "Preferences")
        self.assertEqual(result.extraction_tier, 1)

    def test_learn_with_tier2(self):
        """Test learning with Tier 2 LLM extraction."""
        self.client.post.return_value = {
            "id": "mem-123",
            "text": "Complex text",
            "extracted_metadata": {
                "category": "Technical",
                "confidence": 0.98,
            },
            "extraction_tier": 2,
            "extraction_method": "llm",
        }

        result = self.api.learn("Complex text", tier=2, sync=True)

        self.assertEqual(result.extraction_tier, 2)
        self.assertEqual(result.extraction_method, "llm")

    def test_search(self):
        """Test semantic search."""
        self.client.post.return_value = {
            "memories": [
                {
                    "id": "mem-1",
                    "text": "Result 1",
                    "base_similarity": 0.95,
                    "weighted_score": 1.2,
                    "boosted_by_usage": True,
                },
            ],
        }

        result = self.api.search("query", weight_by_usage=True)

        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], SearchResult)
        self.assertTrue(result[0].boosted_by_usage)

    def test_search_validates_query(self):
        """Test that search validates query."""
        with self.assertRaises(ValidationError):
            self.api.search("")

    def test_recall(self):
        """Test organized recall."""
        self.client.post.return_value = {
            "memories": [
                {"id": "mem-1", "text": "Memory 1", "score": 0.9},
            ],
            "categories": {
                "General": {"summary": "General context", "count": 1},
            },
        }

        result = self.api.recall("query", organized=True)

        self.assertIsInstance(result, RecallResult)
        self.assertEqual(len(result.memories), 1)
        self.assertIn("General", result.categories)

    def test_feedback(self):
        """Test helpfulness feedback."""
        self.client.post.return_value = {"helpfulness_score": 0.7}

        result = self.api.feedback("mem-123", helpful=True)

        self.assertEqual(result["helpfulness_score"], 0.7)

    def test_batch_create(self):
        """Test batch memory creation."""
        self.client.post.return_value = {
            "memories": [
                {"id": "mem-1", "text": "Memory 1"},
                {"id": "mem-2", "text": "Memory 2"},
            ],
        }

        result = self.api.batch_create([
            {"text": "Memory 1"},
            {"text": "Memory 2"},
        ])

        self.assertEqual(len(result), 2)

    def test_batch_create_validates_input(self):
        """Test that batch_create validates input."""
        with self.assertRaises(ValidationError):
            self.api.batch_create([])

        with self.assertRaises(ValidationError):
            self.api.batch_create([{"no_text": "missing"}])


if __name__ == "__main__":
    unittest.main()
