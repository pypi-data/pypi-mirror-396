"""Tests for learn() and organized recall functionality"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json

from recallbricks_langchain import RecallBricksMemory


class TestLearnMethod(unittest.TestCase):
    """Tests for the learn() method with automatic metadata extraction"""

    def setUp(self):
        """Set up test fixtures"""
        self.api_key = "test-api-key"
        self.agent_id = "test-agent"

    @patch('recallbricks_langchain.memory.get_session')
    def test_save_context_uses_learn_endpoint(self, mock_get_session):
        """Test that save_context uses the /memories/learn endpoint"""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"id": "memory-1", "metadata": {"tags": ["test"]}}
        mock_response.raise_for_status = Mock()
        mock_session.post.return_value = mock_response
        mock_get_session.return_value = mock_session

        memory = RecallBricksMemory(
            api_key=self.api_key,
            agent_id=self.agent_id
        )

        memory.save_context(
            {"input": "What is RecallBricks?"},
            {"output": "A cognitive memory platform"}
        )

        # Verify learn endpoint was called twice (once for input, once for output)
        calls = mock_session.post.call_args_list
        self.assertEqual(len(calls), 2)

        # Check that both calls went to /memories/learn
        for call in calls:
            url = call[0][0] if call[0] else call[1].get('url', '')
            if not url:
                # URL might be in kwargs
                url = call.kwargs.get('url', '')
            self.assertIn('/memories/learn', url)

    @patch('recallbricks_langchain.memory.get_session')
    def test_save_context_formats_user_message(self, mock_get_session):
        """Test that save_context formats user message correctly"""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"id": "memory-1"}
        mock_response.raise_for_status = Mock()
        mock_session.post.return_value = mock_response
        mock_get_session.return_value = mock_session

        memory = RecallBricksMemory(
            api_key=self.api_key,
            agent_id=self.agent_id
        )

        memory.save_context(
            {"input": "Hello world"},
            {"output": "Hi there!"}
        )

        # First call should be for user message
        first_call = mock_session.post.call_args_list[0]
        payload = first_call.kwargs.get('json', first_call[1].get('json', {}))
        self.assertIn("User:", payload.get("text", ""))

        # Second call should be for assistant message
        second_call = mock_session.post.call_args_list[1]
        payload = second_call.kwargs.get('json', second_call[1].get('json', {}))
        self.assertIn("Assistant:", payload.get("text", ""))

    @patch('recallbricks_langchain.memory.get_session')
    def test_learn_method_public_api(self, mock_get_session):
        """Test the public learn() method"""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "memory-123",
            "metadata": {
                "tags": ["preferences", "ui"],
                "category": "Settings",
                "importance": 0.8
            }
        }
        mock_response.raise_for_status = Mock()
        mock_session.post.return_value = mock_response
        mock_get_session.return_value = mock_session

        memory = RecallBricksMemory(
            api_key=self.api_key,
            agent_id=self.agent_id
        )

        result = memory.learn("User prefers dark mode")

        # Verify response
        self.assertEqual(result["id"], "memory-123")
        self.assertIn("tags", result["metadata"])

        # Verify correct endpoint
        call_args = mock_session.post.call_args
        url = call_args[0][0] if call_args[0] else call_args.kwargs.get('url', '')
        self.assertIn('/memories/learn', url)

    @patch('recallbricks_langchain.memory.get_session')
    def test_learn_with_custom_source(self, mock_get_session):
        """Test learn() with custom source parameter"""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"id": "memory-1"}
        mock_response.raise_for_status = Mock()
        mock_session.post.return_value = mock_response
        mock_get_session.return_value = mock_session

        memory = RecallBricksMemory(
            api_key=self.api_key,
            agent_id=self.agent_id,
            source="custom-source"
        )

        memory.learn("Test memory", source="override-source")

        call_args = mock_session.post.call_args
        payload = call_args.kwargs.get('json', call_args[1].get('json', {}))
        self.assertEqual(payload["source"], "override-source")

    @patch('recallbricks_langchain.memory.get_session')
    def test_learn_with_project_id(self, mock_get_session):
        """Test learn() includes project_id when set"""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"id": "memory-1"}
        mock_response.raise_for_status = Mock()
        mock_session.post.return_value = mock_response
        mock_get_session.return_value = mock_session

        memory = RecallBricksMemory(
            api_key=self.api_key,
            agent_id=self.agent_id,
            project_id="test-project"
        )

        memory.learn("Test memory")

        call_args = mock_session.post.call_args
        payload = call_args.kwargs.get('json', call_args[1].get('json', {}))
        self.assertEqual(payload["project_id"], "test-project")


class TestOrganizedRecall(unittest.TestCase):
    """Tests for organized recall functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.api_key = "test-api-key"
        self.agent_id = "test-agent"

    @patch('recallbricks_langchain.memory.get_session')
    def test_load_memory_uses_recall_endpoint(self, mock_get_session):
        """Test that load_memory_variables uses /memories/recall endpoint"""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "memories": [],
            "categories": {}
        }
        mock_response.raise_for_status = Mock()
        mock_session.post.return_value = mock_response
        mock_get_session.return_value = mock_session

        memory = RecallBricksMemory(
            api_key=self.api_key,
            agent_id=self.agent_id
        )

        memory.load_memory_variables({"input": "test query"})

        call_args = mock_session.post.call_args
        url = call_args[0][0] if call_args[0] else call_args.kwargs.get('url', '')
        self.assertIn('/memories/recall', url)

    @patch('recallbricks_langchain.memory.get_session')
    def test_organized_recall_enabled_by_default(self, mock_get_session):
        """Test that organized recall is enabled by default"""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"memories": [], "categories": {}}
        mock_response.raise_for_status = Mock()
        mock_session.post.return_value = mock_response
        mock_get_session.return_value = mock_session

        memory = RecallBricksMemory(
            api_key=self.api_key,
            agent_id=self.agent_id
        )

        memory.load_memory_variables({"input": "test"})

        call_args = mock_session.post.call_args
        payload = call_args.kwargs.get('json', call_args[1].get('json', {}))
        self.assertTrue(payload.get("organized", False))

    @patch('recallbricks_langchain.memory.get_session')
    def test_organized_recall_can_be_disabled(self, mock_get_session):
        """Test that organized recall can be disabled"""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"memories": [], "categories": {}}
        mock_response.raise_for_status = Mock()
        mock_session.post.return_value = mock_response
        mock_get_session.return_value = mock_session

        memory = RecallBricksMemory(
            api_key=self.api_key,
            agent_id=self.agent_id,
            organized=False
        )

        memory.load_memory_variables({"input": "test"})

        call_args = mock_session.post.call_args
        payload = call_args.kwargs.get('json', call_args[1].get('json', {}))
        self.assertFalse(payload.get("organized", True))

    @patch('recallbricks_langchain.memory.get_session')
    def test_format_organized_memories(self, mock_get_session):
        """Test that organized memories are formatted correctly"""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "memories": [
                {
                    "id": "1",
                    "text": "User prefers dark mode",
                    "score": 0.95,
                    "metadata": {
                        "category": "Preferences",
                        "tags": ["ui", "settings"]
                    }
                },
                {
                    "id": "2",
                    "text": "User works on Python projects",
                    "score": 0.88,
                    "metadata": {
                        "category": "Work",
                        "tags": ["programming"]
                    }
                }
            ],
            "categories": {
                "Preferences": {
                    "summary": "User UI preferences",
                    "count": 1,
                    "avg_score": 0.95
                },
                "Work": {
                    "summary": "Work-related information",
                    "count": 1,
                    "avg_score": 0.88
                }
            }
        }
        mock_response.raise_for_status = Mock()
        mock_session.post.return_value = mock_response
        mock_get_session.return_value = mock_session

        memory = RecallBricksMemory(
            api_key=self.api_key,
            agent_id=self.agent_id,
            organized=True
        )

        result = memory.load_memory_variables({"input": "user preferences"})

        history = result["history"][0]
        # Check for category structure in output
        self.assertIn("=== Relevant Context ===", history)
        self.assertIn("Preferences", history)
        self.assertIn("Work", history)

    @patch('recallbricks_langchain.memory.get_session')
    def test_recall_method_public_api(self, mock_get_session):
        """Test the public recall() method"""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "memories": [{"id": "1", "text": "Test memory", "score": 0.9}],
            "categories": {"General": {"summary": "Test", "count": 1, "avg_score": 0.9}}
        }
        mock_response.raise_for_status = Mock()
        mock_session.post.return_value = mock_response
        mock_get_session.return_value = mock_session

        memory = RecallBricksMemory(
            api_key=self.api_key,
            agent_id=self.agent_id
        )

        result = memory.recall("test query", limit=5, organized=True)

        self.assertIn("memories", result)
        self.assertIn("categories", result)
        self.assertEqual(len(result["memories"]), 1)


class TestNewParameters(unittest.TestCase):
    """Tests for new initialization parameters"""

    def test_organized_parameter_default(self):
        """Test organized parameter defaults to True"""
        memory = RecallBricksMemory(
            api_key="test-key",
            agent_id="test-agent"
        )
        self.assertTrue(memory.organized)

    def test_source_parameter_default(self):
        """Test source parameter defaults to 'langchain'"""
        memory = RecallBricksMemory(
            api_key="test-key",
            agent_id="test-agent"
        )
        self.assertEqual(memory.source, "langchain")

    def test_source_parameter_custom(self):
        """Test custom source parameter"""
        memory = RecallBricksMemory(
            api_key="test-key",
            agent_id="test-agent",
            source="my-custom-source"
        )
        self.assertEqual(memory.source, "my-custom-source")

    def test_project_id_parameter(self):
        """Test project_id parameter"""
        memory = RecallBricksMemory(
            api_key="test-key",
            agent_id="test-agent",
            project_id="my-project"
        )
        self.assertEqual(memory.project_id, "my-project")

    def test_project_id_default_none(self):
        """Test project_id defaults to None"""
        memory = RecallBricksMemory(
            api_key="test-key",
            agent_id="test-agent"
        )
        self.assertIsNone(memory.project_id)


if __name__ == '__main__':
    unittest.main()
