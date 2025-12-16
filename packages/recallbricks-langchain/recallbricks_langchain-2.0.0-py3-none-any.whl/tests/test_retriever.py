"""Tests for RecallBricksRetriever"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from langchain_core.documents import Document

from recallbricks_langchain import RecallBricksRetriever
from recallbricks_langchain.memory import ValidationError, RateLimitError


class TestRecallBricksRetriever(unittest.TestCase):
    """Test suite for RecallBricksRetriever"""

    def setUp(self):
        """Set up test fixtures"""
        self.api_key = "test-api-key"

    def test_initialization(self):
        """Test basic initialization"""
        retriever = RecallBricksRetriever(api_key=self.api_key)

        self.assertEqual(retriever.api_key, self.api_key)
        self.assertEqual(retriever.k, 4)
        self.assertTrue(retriever.organized)
        self.assertIsNone(retriever.project_id)

    def test_initialization_with_custom_k(self):
        """Test initialization with custom k parameter"""
        retriever = RecallBricksRetriever(
            api_key=self.api_key,
            k=10
        )

        self.assertEqual(retriever.k, 10)

    def test_initialization_with_project_id(self):
        """Test initialization with project_id"""
        retriever = RecallBricksRetriever(
            api_key=self.api_key,
            project_id="test-project"
        )

        self.assertEqual(retriever.project_id, "test-project")

    def test_initialization_requires_api_key(self):
        """Test that api_key is required"""
        with self.assertRaises(ValidationError):
            RecallBricksRetriever(api_key="")

    def test_initialization_requires_https(self):
        """Test that HTTPS is required"""
        with self.assertRaises(ValidationError):
            RecallBricksRetriever(
                api_key=self.api_key,
                api_url="http://api.example.com"
            )

    def test_initialization_validates_k_range(self):
        """Test that k must be between 1 and 100"""
        with self.assertRaises(ValidationError):
            RecallBricksRetriever(api_key=self.api_key, k=0)

        with self.assertRaises(ValidationError):
            RecallBricksRetriever(api_key=self.api_key, k=101)

    @patch('recallbricks_langchain.retriever.get_session')
    def test_get_relevant_documents(self, mock_get_session):
        """Test retrieving documents"""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "memories": [
                {
                    "id": "1",
                    "text": "Test memory content",
                    "score": 0.95,
                    "metadata": {
                        "tags": ["test", "memory"],
                        "category": "General",
                        "importance": 0.8,
                        "entities": ["test"]
                    },
                    "created_at": "2024-01-01T00:00:00Z"
                }
            ],
            "categories": {}
        }
        mock_response.raise_for_status = Mock()
        mock_session.post.return_value = mock_response
        mock_get_session.return_value = mock_session

        retriever = RecallBricksRetriever(api_key=self.api_key)

        # Use invoke() for LangChain v0.2+ compatibility
        docs = retriever.invoke("test query")

        self.assertEqual(len(docs), 1)
        self.assertIsInstance(docs[0], Document)
        self.assertEqual(docs[0].page_content, "Test memory content")

    @patch('recallbricks_langchain.retriever.get_session')
    def test_document_metadata(self, mock_get_session):
        """Test that documents have correct metadata"""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "memories": [
                {
                    "id": "memory-123",
                    "text": "Test content",
                    "score": 0.92,
                    "metadata": {
                        "tags": ["important"],
                        "category": "Work",
                        "importance": 0.9,
                        "entities": ["project"]
                    },
                    "created_at": "2024-01-15T10:30:00Z"
                }
            ],
            "categories": {}
        }
        mock_response.raise_for_status = Mock()
        mock_session.post.return_value = mock_response
        mock_get_session.return_value = mock_session

        retriever = RecallBricksRetriever(api_key=self.api_key)

        docs = retriever.invoke("test")

        doc = docs[0]
        self.assertEqual(doc.metadata["score"], 0.92)
        self.assertEqual(doc.metadata["memory_id"], "memory-123")
        self.assertEqual(doc.metadata["tags"], ["important"])
        self.assertEqual(doc.metadata["category"], "Work")
        self.assertEqual(doc.metadata["importance"], 0.9)
        self.assertEqual(doc.metadata["entities"], ["project"])
        self.assertEqual(doc.metadata["created_at"], "2024-01-15T10:30:00Z")

    @patch('recallbricks_langchain.retriever.get_session')
    def test_uses_recall_endpoint(self, mock_get_session):
        """Test that retriever uses /memories/recall endpoint"""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"memories": [], "categories": {}}
        mock_response.raise_for_status = Mock()
        mock_session.post.return_value = mock_response
        mock_get_session.return_value = mock_session

        retriever = RecallBricksRetriever(api_key=self.api_key)

        retriever.invoke("test")

        call_args = mock_session.post.call_args
        url = call_args[0][0] if call_args[0] else call_args.kwargs.get('url', '')
        self.assertIn('/memories/recall', url)

    @patch('recallbricks_langchain.retriever.get_session')
    def test_uses_organized_by_default(self, mock_get_session):
        """Test that organized recall is used by default"""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"memories": [], "categories": {}}
        mock_response.raise_for_status = Mock()
        mock_session.post.return_value = mock_response
        mock_get_session.return_value = mock_session

        retriever = RecallBricksRetriever(api_key=self.api_key)

        retriever.invoke("test")

        call_args = mock_session.post.call_args
        payload = call_args.kwargs.get('json', call_args[1].get('json', {}))
        self.assertTrue(payload.get("organized"))

    @patch('recallbricks_langchain.retriever.get_session')
    def test_organized_can_be_disabled(self, mock_get_session):
        """Test that organized recall can be disabled"""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"memories": [], "categories": {}}
        mock_response.raise_for_status = Mock()
        mock_session.post.return_value = mock_response
        mock_get_session.return_value = mock_session

        retriever = RecallBricksRetriever(
            api_key=self.api_key,
            organized=False
        )

        retriever.invoke("test")

        call_args = mock_session.post.call_args
        payload = call_args.kwargs.get('json', call_args[1].get('json', {}))
        self.assertFalse(payload.get("organized"))

    @patch('recallbricks_langchain.retriever.get_session')
    def test_respects_k_parameter(self, mock_get_session):
        """Test that k parameter is passed to API"""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"memories": [], "categories": {}}
        mock_response.raise_for_status = Mock()
        mock_session.post.return_value = mock_response
        mock_get_session.return_value = mock_session

        retriever = RecallBricksRetriever(
            api_key=self.api_key,
            k=7
        )

        retriever.invoke("test")

        call_args = mock_session.post.call_args
        payload = call_args.kwargs.get('json', call_args[1].get('json', {}))
        self.assertEqual(payload.get("limit"), 7)

    @patch('recallbricks_langchain.retriever.get_session')
    def test_project_id_in_payload(self, mock_get_session):
        """Test that project_id is included in API payload"""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"memories": [], "categories": {}}
        mock_response.raise_for_status = Mock()
        mock_session.post.return_value = mock_response
        mock_get_session.return_value = mock_session

        retriever = RecallBricksRetriever(
            api_key=self.api_key,
            project_id="my-project"
        )

        retriever.invoke("test")

        call_args = mock_session.post.call_args
        payload = call_args.kwargs.get('json', call_args[1].get('json', {}))
        self.assertEqual(payload.get("project_id"), "my-project")


class TestRetrieverWithCategories(unittest.TestCase):
    """Test retriever category-aware features"""

    @patch('recallbricks_langchain.retriever.get_session')
    def test_get_documents_with_categories(self, mock_get_session):
        """Test get_relevant_documents_with_categories method"""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "memories": [
                {
                    "id": "1",
                    "text": "User likes Python",
                    "score": 0.95,
                    "metadata": {"category": "Preferences", "tags": ["programming"]}
                }
            ],
            "categories": {
                "Preferences": {
                    "summary": "User programming preferences",
                    "count": 1,
                    "avg_score": 0.95
                }
            }
        }
        mock_response.raise_for_status = Mock()
        mock_session.post.return_value = mock_response
        mock_get_session.return_value = mock_session

        retriever = RecallBricksRetriever(api_key="test-key")

        result = retriever.get_relevant_documents_with_categories("user preferences")

        self.assertIn("documents", result)
        self.assertIn("categories", result)
        self.assertEqual(len(result["documents"]), 1)
        self.assertIn("Preferences", result["categories"])

    @patch('recallbricks_langchain.retriever.get_session')
    def test_with_categories_forces_organized(self, mock_get_session):
        """Test that get_relevant_documents_with_categories forces organized=True"""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"memories": [], "categories": {}}
        mock_response.raise_for_status = Mock()
        mock_session.post.return_value = mock_response
        mock_get_session.return_value = mock_session

        # Even with organized=False on init
        retriever = RecallBricksRetriever(
            api_key="test-key",
            organized=False
        )

        retriever.get_relevant_documents_with_categories("test")

        call_args = mock_session.post.call_args
        payload = call_args.kwargs.get('json', call_args[1].get('json', {}))
        # Should be True for this method
        self.assertTrue(payload.get("organized"))


class TestRetrieverEmptyResults(unittest.TestCase):
    """Test retriever with empty results"""

    @patch('recallbricks_langchain.retriever.get_session')
    def test_empty_memories_returns_empty_list(self, mock_get_session):
        """Test that empty memories returns empty document list"""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {"memories": [], "categories": {}}
        mock_response.raise_for_status = Mock()
        mock_session.post.return_value = mock_response
        mock_get_session.return_value = mock_session

        retriever = RecallBricksRetriever(api_key="test-key")

        docs = retriever.invoke("nonexistent query")

        self.assertEqual(docs, [])


if __name__ == '__main__':
    unittest.main()
