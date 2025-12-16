"""Tests for RecallBricksChatMessageHistory"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from langchain_core.messages import HumanMessage, AIMessage

from recallbricks_langchain import RecallBricksChatMessageHistory
from recallbricks_langchain.memory import ValidationError, RateLimitError


class TestRecallBricksChatMessageHistory(unittest.TestCase):
    """Test suite for RecallBricksChatMessageHistory"""

    def setUp(self):
        """Set up test fixtures"""
        self.api_key = "test-api-key"
        self.session_id = "test-session-123"

    def test_initialization(self):
        """Test basic initialization"""
        history = RecallBricksChatMessageHistory(
            api_key=self.api_key,
            session_id=self.session_id
        )

        self.assertEqual(history.api_key, self.api_key)
        self.assertEqual(history.session_id, self.session_id)
        self.assertIsNone(history.project_id)

    def test_initialization_with_project_id(self):
        """Test initialization with project_id"""
        history = RecallBricksChatMessageHistory(
            api_key=self.api_key,
            session_id=self.session_id,
            project_id="test-project"
        )

        self.assertEqual(history.project_id, "test-project")

    def test_initialization_requires_api_key(self):
        """Test that api_key is required"""
        with self.assertRaises(ValidationError):
            RecallBricksChatMessageHistory(
                api_key="",
                session_id=self.session_id
            )

    def test_initialization_requires_session_id(self):
        """Test that session_id is required"""
        with self.assertRaises(ValidationError):
            RecallBricksChatMessageHistory(
                api_key=self.api_key,
                session_id=""
            )

    def test_initialization_requires_https(self):
        """Test that HTTPS is required for api_url"""
        with self.assertRaises(ValidationError):
            RecallBricksChatMessageHistory(
                api_key=self.api_key,
                session_id=self.session_id,
                api_url="http://api.example.com"
            )

    @patch('recallbricks_langchain.chat_history.get_session')
    def test_add_human_message(self, mock_get_session):
        """Test adding a human message"""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"id": "memory-1"}
        mock_response.raise_for_status = Mock()
        mock_session.post.return_value = mock_response
        mock_get_session.return_value = mock_session

        history = RecallBricksChatMessageHistory(
            api_key=self.api_key,
            session_id=self.session_id
        )

        history.add_user_message("Hello, world!")

        # Verify API was called
        call_args = mock_session.post.call_args
        url = call_args[0][0] if call_args[0] else call_args.kwargs.get('url', '')
        self.assertIn('/memories/learn', url)

        # Verify payload contains human prefix
        payload = call_args.kwargs.get('json', call_args[1].get('json', {}))
        self.assertIn("human:", payload.get("text", ""))

    @patch('recallbricks_langchain.chat_history.get_session')
    def test_add_ai_message(self, mock_get_session):
        """Test adding an AI message"""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"id": "memory-1"}
        mock_response.raise_for_status = Mock()
        mock_session.post.return_value = mock_response
        mock_get_session.return_value = mock_session

        history = RecallBricksChatMessageHistory(
            api_key=self.api_key,
            session_id=self.session_id
        )

        history.add_ai_message("Hello! How can I help?")

        # Verify payload contains ai prefix
        call_args = mock_session.post.call_args
        payload = call_args.kwargs.get('json', call_args[1].get('json', {}))
        self.assertIn("ai:", payload.get("text", ""))

    @patch('recallbricks_langchain.chat_history.get_session')
    def test_add_message_includes_session_metadata(self, mock_get_session):
        """Test that messages include session metadata"""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"id": "memory-1"}
        mock_response.raise_for_status = Mock()
        mock_session.post.return_value = mock_response
        mock_get_session.return_value = mock_session

        history = RecallBricksChatMessageHistory(
            api_key=self.api_key,
            session_id=self.session_id
        )

        history.add_user_message("Test message")

        call_args = mock_session.post.call_args
        payload = call_args.kwargs.get('json', call_args[1].get('json', {}))

        self.assertIn("metadata", payload)
        self.assertEqual(payload["metadata"]["session_id"], self.session_id)
        self.assertEqual(payload["metadata"]["message_type"], "human")

    @patch('recallbricks_langchain.chat_history.get_session')
    def test_add_message_uses_correct_source(self, mock_get_session):
        """Test that messages use session-specific source"""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"id": "memory-1"}
        mock_response.raise_for_status = Mock()
        mock_session.post.return_value = mock_response
        mock_get_session.return_value = mock_session

        history = RecallBricksChatMessageHistory(
            api_key=self.api_key,
            session_id=self.session_id
        )

        history.add_user_message("Test")

        call_args = mock_session.post.call_args
        payload = call_args.kwargs.get('json', call_args[1].get('json', {}))

        self.assertEqual(payload["source"], f"langchain-session-{self.session_id}")

    @patch('recallbricks_langchain.chat_history.get_session')
    def test_messages_property_loads_on_first_access(self, mock_get_session):
        """Test that messages are loaded from API on first access"""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "memories": [
                {
                    "text": "human: Hello",
                    "metadata": {"message_type": "human"}
                },
                {
                    "text": "ai: Hi there!",
                    "metadata": {"message_type": "ai"}
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_session.post.return_value = mock_response
        mock_get_session.return_value = mock_session

        history = RecallBricksChatMessageHistory(
            api_key=self.api_key,
            session_id=self.session_id
        )

        messages = history.messages

        # Verify API was called
        self.assertTrue(mock_session.post.called)
        call_args = mock_session.post.call_args
        url = call_args[0][0] if call_args[0] else call_args.kwargs.get('url', '')
        self.assertIn('/memories/recall', url)

    @patch('recallbricks_langchain.chat_history.get_session')
    def test_messages_converted_to_correct_types(self, mock_get_session):
        """Test that loaded messages are converted to correct types"""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "memories": [
                {
                    "text": "human: Hello",
                    "metadata": {"message_type": "human"}
                },
                {
                    "text": "ai: Hi there!",
                    "metadata": {"message_type": "ai"}
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_session.post.return_value = mock_response
        mock_get_session.return_value = mock_session

        history = RecallBricksChatMessageHistory(
            api_key=self.api_key,
            session_id=self.session_id
        )

        messages = history.messages

        self.assertEqual(len(messages), 2)
        self.assertIsInstance(messages[0], HumanMessage)
        self.assertIsInstance(messages[1], AIMessage)

    def test_clear_resets_local_cache(self):
        """Test that clear resets the local message cache"""
        history = RecallBricksChatMessageHistory(
            api_key=self.api_key,
            session_id=self.session_id
        )

        # Manually set some state
        history._messages = [HumanMessage(content="Test")]
        history._loaded = True

        history.clear()

        self.assertEqual(history._messages, [])
        self.assertFalse(history._loaded)

    @patch('recallbricks_langchain.chat_history.get_session')
    def test_add_message_updates_local_cache(self, mock_get_session):
        """Test that adding a message updates local cache"""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"id": "memory-1"}
        mock_response.raise_for_status = Mock()
        mock_session.post.return_value = mock_response
        mock_get_session.return_value = mock_session

        history = RecallBricksChatMessageHistory(
            api_key=self.api_key,
            session_id=self.session_id
        )

        history.add_user_message("Test message")

        self.assertEqual(len(history._messages), 1)
        self.assertIsInstance(history._messages[0], HumanMessage)
        self.assertEqual(history._messages[0].content, "Test message")


class TestChatHistoryWithProjectId(unittest.TestCase):
    """Test chat history with project_id"""

    @patch('recallbricks_langchain.chat_history.get_session')
    def test_add_message_includes_project_id(self, mock_get_session):
        """Test that project_id is included in API calls"""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"id": "memory-1"}
        mock_response.raise_for_status = Mock()
        mock_session.post.return_value = mock_response
        mock_get_session.return_value = mock_session

        history = RecallBricksChatMessageHistory(
            api_key="test-key",
            session_id="test-session",
            project_id="test-project"
        )

        history.add_user_message("Test")

        call_args = mock_session.post.call_args
        payload = call_args.kwargs.get('json', call_args[1].get('json', {}))

        self.assertEqual(payload.get("project_id"), "test-project")

    @patch('recallbricks_langchain.chat_history.get_session')
    def test_load_messages_includes_project_id(self, mock_get_session):
        """Test that project_id is included when loading messages"""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"memories": []}
        mock_response.raise_for_status = Mock()
        mock_session.post.return_value = mock_response
        mock_get_session.return_value = mock_session

        history = RecallBricksChatMessageHistory(
            api_key="test-key",
            session_id="test-session",
            project_id="test-project"
        )

        _ = history.messages

        call_args = mock_session.post.call_args
        payload = call_args.kwargs.get('json', call_args[1].get('json', {}))

        self.assertEqual(payload.get("project_id"), "test-project")


if __name__ == '__main__':
    unittest.main()
